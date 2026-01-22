"""
天气上下文（可选）

使用 Open-Meteo 提供天气信息，支持两级缓存：
- 地理编码缓存（30天）
- 天气缓存（15分钟）

输出格式：例如 "12℃，多云，风1.0m/s" 或 "12℃，多云，风1.0m/s(东北)"
"""

from __future__ import annotations

import datetime
from typing import Optional

# config 作为默认兜底：字段可能不存在，需 getattr 安全读取
import config as _config
from core import settings as app_settings
from .weather_open_meteo import get_weather_string

WEATHER_ENABLED = bool(getattr(_config, "WEATHER_ENABLED", False))
WEATHER_PROVIDER = str(getattr(_config, "WEATHER_PROVIDER", "openweather"))
WEATHER_TIMEOUT_SECONDS = int(getattr(_config, "WEATHER_TIMEOUT_SECONDS", 5))
DEBUG = bool(getattr(_config, "DEBUG", False))

# 简单的内存缓存（按天+城市）
_weather_cache: dict[str, str] = {"date": "", "city": "", "value": ""}


def get_weather_summary(city: str) -> str:
    """
    获取天气简述（例如：'12℃，多云，风1.0m/s' 或 '12℃，多云，风1.0m/s(东北)'）

    实现逻辑：
    - 若 WEATHER_ENABLED=False 或 city 为空 → 返回空字符串
    - 使用 Open-Meteo API（无需 API Key）
    - 带两级缓存：地理编码（30天）+ 天气（15分钟）
    - 为了不影响主流程，任何异常都会被吞掉并返回空字符串
    """
    # 检查是否启用天气
    try:
        enabled = app_settings.get_weather_enabled()
    except Exception:
        enabled = WEATHER_ENABLED

    if not enabled:
        return ""

    city = (city or "").strip()
    if not city:
        return ""

    # 简单的内存缓存（按天+城市，避免频繁调用）
    today = datetime.date.today().isoformat()
    if _weather_cache["date"] == today and _weather_cache["city"] == city:
        return _weather_cache["value"]

    # 调用 Open-Meteo 实现
    try:
        summary = get_weather_string(city)
    except Exception as e:
        if DEBUG:
            print(f"[Context] 获取天气失败: {e}")
        summary = ""

    # 更新内存缓存
    _weather_cache["date"] = today
    _weather_cache["city"] = city
    _weather_cache["value"] = summary

    return summary

