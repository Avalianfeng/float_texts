"""
天气上下文（可选）

Phase D：为了不引入额外复杂度，当前实现为“可关闭”的空实现：
- WEATHER_ENABLED=False 时不做任何事
- 即便开启，由于缺省不配置 API Key，仍会静默返回空字符串

后续如果你选定具体天气服务（如 OpenWeather/和风天气），
可以在此模块补全 get_weather_summary 的实现。
"""

from __future__ import annotations

import datetime
from typing import Optional

import requests  # 预留给未来天气 API

# config 作为默认兜底：字段可能不存在，需 getattr 安全读取
import config as _config

WEATHER_ENABLED = bool(getattr(_config, "WEATHER_ENABLED", False))
WEATHER_PROVIDER = str(getattr(_config, "WEATHER_PROVIDER", "openweather"))
WEATHER_API_KEY = str(getattr(_config, "WEATHER_API_KEY", ""))
WEATHER_TIMEOUT_SECONDS = int(getattr(_config, "WEATHER_TIMEOUT_SECONDS", 5))
DEBUG = bool(getattr(_config, "DEBUG", False))

_weather_cache: dict[str, str] = {"date": "", "city": "", "value": ""}


def get_weather_summary(city: str) -> str:
    """
    获取天气简述（例如：'多云 12~18℃' 或 '小雨 8℃'）

    当前实现：
    - 若 WEATHER_ENABLED=False 或 city 为空 → 返回空字符串
    - 若未配置 API Key → 返回空字符串
    - 为了不影响主流程，任何异常都会被吞掉并返回空字符串
    """
    if not WEATHER_ENABLED:
        return ""

    city = (city or "").strip()
    if not city:
        return ""

    today = datetime.date.today().isoformat()
    if _weather_cache["date"] == today and _weather_cache["city"] == city:
        return _weather_cache["value"]

    if not WEATHER_API_KEY:
        if DEBUG:
            print("[Context] WEATHER_ENABLED=True 但未配置 WEATHER_API_KEY，返回空天气")
        return ""

    # 预留：简单示例结构，未真正调用具体天气 API，以免引入不稳定因素
    # 未来你可以在这里实现实际的 HTTP 调用逻辑
    try:
        if DEBUG:
            print(f"[Context] WEATHER_PROVIDER={WEATHER_PROVIDER} 暂未实现具体 API，返回空天气")
        summary = ""
    except Exception as e:
        if DEBUG:
            print(f"[Context] 获取天气失败: {e}")
        summary = ""

    _weather_cache["date"] = today
    _weather_cache["city"] = city
    _weather_cache["value"] = summary
    return summary

