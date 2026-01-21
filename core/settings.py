"""
应用设置（QSettings 封装）

目标：
- 不写回 config.py（config 仅作为默认值兜底）
- API Key 等敏感信息保存在本机（Windows 注册表 / macOS plist / Linux ini）
- 提供 typed getters/setters，避免散落全项目直接用 QSettings
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from PyQt6.QtCore import QSettings

# config 作为默认兜底，但不要强依赖某些字段一定存在（避免 ImportError）
import config as _config


APP_ORG = "FloatWords"
APP_NAME = "FloatWords"


class Keys:
    AI_ENABLED = "ai/enabled"
    AI_TEXT_SOURCE = "ai/text_source"  # auto/local/ai
    AI_DEEPSEEK_API_KEY = "ai/deepseek_api_key"
    CONTEXT_CITY = "context/city"
    CONTEXT_LOCATION_MODE = "context/location_mode"  # manual/ip
    IDLE_ENABLED = "idle/enabled"
    IDLE_THRESHOLD_SECONDS = "idle/threshold_seconds"


def _qs() -> QSettings:
    return QSettings(APP_ORG, APP_NAME)


def get_bool(key: str, default: bool) -> bool:
    try:
        v = _qs().value(key, default)
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        s = str(v).strip().lower()
        return s in ("1", "true", "yes", "y", "on")
    except Exception:
        return default


def get_int(key: str, default: int) -> int:
    try:
        v = _qs().value(key, default)
        return int(v)
    except Exception:
        return default


def get_str(key: str, default: str) -> str:
    try:
        v = _qs().value(key, default)
        return "" if v is None else str(v)
    except Exception:
        return default


def set_value(key: str, value: Any) -> None:
    _qs().setValue(key, value)


# -------- typed accessors --------


def get_ai_enabled() -> bool:
    return get_bool(Keys.AI_ENABLED, bool(getattr(_config, "AI_ENABLED", True)))


def set_ai_enabled(v: bool) -> None:
    set_value(Keys.AI_ENABLED, bool(v))


def get_text_source() -> str:
    default = str(getattr(_config, "TEXT_SOURCE", "auto"))
    v = get_str(Keys.AI_TEXT_SOURCE, default).lower()
    return v if v in ("auto", "local", "ai") else default


def set_text_source(v: str) -> None:
    set_value(Keys.AI_TEXT_SOURCE, (v or "").lower())


def get_deepseek_api_key() -> str:
    # 注意：环境变量优先级不在这里处理（调用方做 env > settings > config）
    return get_str(Keys.AI_DEEPSEEK_API_KEY, "")


def set_deepseek_api_key(v: str) -> None:
    set_value(Keys.AI_DEEPSEEK_API_KEY, (v or "").strip())


def get_city() -> str:
    # settings 优先，其次 config.CITY
    v = get_str(Keys.CONTEXT_CITY, "").strip()
    return v if v else (str(getattr(_config, "CITY", "")) or "")


def set_city(v: str) -> None:
    set_value(Keys.CONTEXT_CITY, (v or "").strip())


def get_location_mode() -> str:
    default = str(getattr(_config, "LOCATION_MODE", "manual") or "manual")
    v = get_str(Keys.CONTEXT_LOCATION_MODE, default).lower()
    return v if v in ("manual", "ip") else "manual"


def set_location_mode(v: str) -> None:
    set_value(Keys.CONTEXT_LOCATION_MODE, (v or "").lower())


def get_idle_only() -> bool:
    return get_bool(Keys.IDLE_ENABLED, bool(getattr(_config, "IDLE_ONLY", True)))


def set_idle_only(v: bool) -> None:
    set_value(Keys.IDLE_ENABLED, bool(v))


def get_idle_threshold_seconds() -> int:
    v = get_int(Keys.IDLE_THRESHOLD_SECONDS, int(getattr(_config, "IDLE_THRESHOLD_SECONDS", 30)))
    return max(0, v)


def set_idle_threshold_seconds(v: int) -> None:
    set_value(Keys.IDLE_THRESHOLD_SECONDS, int(v))

