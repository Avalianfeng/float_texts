"""
DeepSeek AI 文本提供者

通过 OpenAI-compatible Chat Completions 接口生成每日文本，并缓存到本地。
"""

from __future__ import annotations

import datetime
import json
import os
import time
import threading
from typing import List, Dict, Any, Optional

import requests

from .base import BaseTextProvider
from core.context.location import get_city
from core.context.weather import get_weather_summary
from core import settings as app_settings
from config import (
    AI_API_BASE,
    AI_API_KEY,
    AI_MODEL,
    AI_TEMPERATURE,
    AI_ITEMS_PER_DAY,
    AI_CACHE_DIR,
    AI_TIMEOUT_SECONDS,
    DEBUG,
    AI_PROMPT_TEMPLATE,
)


def _today_str() -> str:
    return datetime.date.today().isoformat()


def _get_api_key() -> str:
    """
    API Key 读取优先级：
    1) 环境变量 DEEPSEEK_API_KEY（方便部署/高级用户）
    2) QSettings（SettingsDialog 保存）
    3) config.AI_API_KEY（兜底，通常为空）
    """
    env = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if env:
        return env
    try:
        v = (app_settings.get_deepseek_api_key() or "").strip()
        if v:
            return v
    except Exception:
        pass
    return (AI_API_KEY or "").strip()


class DeepSeekTextProvider(BaseTextProvider):
    """使用 DeepSeek 生成每日文本的 Provider"""

    def __init__(self) -> None:
        super().__init__()
        self._items: List[Dict[str, Any]] = []
        self._session = requests.Session()
        self._last_cache_path: str | None = None
        self._lock = threading.Lock()
        self._preparing: bool = False
        self._last_failure_ts: float | None = None
        self._context: Dict[str, Any] = {}

    @property
    def preparing(self) -> bool:
        return self._preparing

    @property
    def last_failure_ts(self) -> float | None:
        return self._last_failure_ts

    # ---------- 公共接口 ----------

    def prepare(self) -> None:
        """加载今日缓存或从 DeepSeek 生成"""
        # single-flight：避免并发 prepare（只在锁内做状态切换，不要把网络/IO 放锁里）
        with self._lock:
            if self._preparing:
                if DEBUG:
                    print("[AI] prepare 已在进行中，跳过重复调用")
                return
            self._preparing = True

        cache_path = ""

        try:
            self._ensure_cache_dir()
            cache_path = self._get_today_cache_path()
            self._last_cache_path = cache_path

            if os.path.exists(cache_path):
                if DEBUG:
                    print(f"[AI] 发现今日缓存: {cache_path}")
                if self._load_cache(cache_path):
                    self._ready = True
                    return
                else:
                    if DEBUG:
                        print("[AI] 缓存无效，准备重新生成")

            # 没有有效缓存，尝试调用 DeepSeek
            if not _get_api_key():
                if DEBUG:
                    print("[AI] 未配置 AI_API_KEY（请设置环境变量 DEEPSEEK_API_KEY），跳过 AI 生成")
                self._ready = False
                return

            data = self._generate_from_ai()
            if not data:
                self._ready = False
                return

            items = data.get("items") or []
            # 只保留 text 字段
            self._items = [{"text": str(it.get("text", "")).strip()} for it in items if it.get("text")]

            if not self._items:
                if DEBUG:
                    print("[AI] 生成结果为空")
                self._ready = False
                return

            # 写入缓存
            payload = {
                "date": data.get("date") or self._today_str(),
                "context": self._context or {},
                "items": self._items,
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            if DEBUG:
                print(f"[AI] 已写入缓存: {cache_path}")

            self._ready = True
        except Exception as e:
            if DEBUG:
                print(f"[AI] 生成失败: {e}")
            self._ready = False
            self._last_failure_ts = time.time()
        finally:
            with self._lock:
                self._preparing = False

    def get_next_text(self) -> str:
        """从 AI 文本池中取一条"""
        if not self._items:
            return ""
        import random

        return random.choice(self._items).get("text", "")

    def invalidate_today_cache(self) -> None:
        """删除今日缓存并清空当前内容（下次 prepare 会重新生成）"""
        try:
            path = self._last_cache_path or self._get_today_cache_path()
            if os.path.exists(path):
                os.remove(path)
                if DEBUG:
                    print(f"[AI] 已删除今日缓存: {path}")
        except Exception as e:
            if DEBUG:
                print(f"[AI] 删除今日缓存失败: {e}")
        finally:
            self._items = []
            self._ready = False

    # ---------- 内部实现 ----------

    def _ensure_cache_dir(self) -> None:
        os.makedirs(AI_CACHE_DIR, exist_ok=True)

    def _today_str(self) -> str:
        return _today_str()

    def _get_today_cache_path(self) -> str:
        return os.path.join(AI_CACHE_DIR, f"{self._today_str()}.json")

    def _load_cache(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 读取上下文（可选）
            ctx = data.get("context") or {}
            if isinstance(ctx, dict):
                self._context = ctx
            items = data.get("items") or []
            self._items = [{"text": str(it.get("text", "")).strip()} for it in items if it.get("text")]
            if not self._items:
                return False
            return True
        except Exception as e:
            if DEBUG:
                print(f"[AI] 读取缓存失败: {e}")
            return False

    def _build_prompt(self) -> str:
        """构建带上下文的 Prompt"""
        today = datetime.date.today()
        date_str = today.isoformat()
        weekday = ["一", "二", "三", "四", "五", "六", "日"][today.weekday()]

        # 简单划分时间段
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = "早晨"
        elif 12 <= hour < 18:
            time_of_day = "下午"
        elif 18 <= hour < 23:
            time_of_day = "晚上"
        else:
            time_of_day = "深夜"

        # 获取城市和天气（失败时返回空字符串）
        try:
            city = get_city()
        except Exception as e:
            if DEBUG:
                print(f"[Context] 获取城市失败: {e}")
            city = ""

        try:
            weather = get_weather_summary(city) if city else ""
        except Exception as e:
            if DEBUG:
                print(f"[Context] 获取天气失败: {e}")
            weather = ""

        # 保存上下文到实例（用于写入缓存）
        self._context = {
            "date": date_str,
            "weekday": weekday,
            "time_of_day": time_of_day,
            "city": city,
            "weather": weather,
        }

        return AI_PROMPT_TEMPLATE.format(
            n=AI_ITEMS_PER_DAY,
            date=date_str,
            weekday=weekday,
            time_of_day=time_of_day,
            city=city,
            weather=weather,
        )

    def _generate_from_ai(self) -> Optional[Dict[str, Any]]:
        """调用 DeepSeek 接口生成文本"""
        url = AI_API_BASE.rstrip("/") + "/v1/chat/completions"
        if DEBUG:
            proxies = requests.utils.get_environ_proxies(url) or {}
            print(f"[AI] proxies: {proxies if proxies else '(none)'}")
        headers = {
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        }

        prompt = self._build_prompt()

        body = {
            "model": AI_MODEL,
            "temperature": AI_TEMPERATURE,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        if DEBUG:
            print(f"[AI] 调用 DeepSeek: {url}")

        # timeout 分离：connect 5s，read AI_TIMEOUT_SECONDS（默认 20，可在 config 调大）
        resp = self._session.post(url, headers=headers, json=body, timeout=(5, AI_TIMEOUT_SECONDS))
        resp.raise_for_status()
        data = resp.json()

        choices = data.get("choices") or []
        if not choices:
            raise ValueError("AI 返回没有 choices")

        content = choices[0].get("message", {}).get("content", "")
        if DEBUG:
            print("[AI] 原始返回内容截断:", content[:120].replace("\n", " ") + "...")

        # content 应该是 JSON 字符串
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # 尝试从中提取 JSON 片段
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1 or start >= end:
                raise ValueError("AI 返回内容不是有效 JSON")
            json_str = content[start : end + 1]
            result = json.loads(json_str)

        return result

