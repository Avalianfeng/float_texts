"""
位置上下文（城市）

Phase D：先支持 manual 模式（用户在 config 里手动配置 CITY），
后续可扩展 IP 定位。
"""

from __future__ import annotations

import datetime
from typing import Optional

import requests  # 预留给 IP 模式

# config 作为默认兜底：字段可能不存在，需 getattr 安全读取
import config as _config
DEBUG = bool(getattr(_config, "DEBUG", False))
from core import settings as app_settings

_city_cache: dict[str, str] = {"date": "", "value": ""}


def get_city() -> str:
    """
    获取城市名称：
    - manual：直接返回 config.CITY
    - ip：预留，当前实现简化为与 manual 行为一致

    无论何种情况，失败都返回空字符串，不抛异常。
    """
    today = datetime.date.today().isoformat()
    if _city_cache["date"] == today:
        return _city_cache["value"]

    city = ""

    try:
        mode = (app_settings.get_location_mode() or str(getattr(_config, "LOCATION_MODE", "manual")) or "manual").lower()
    except Exception:
        mode = (str(getattr(_config, "LOCATION_MODE", "manual")) or "manual").lower()

    if mode == "manual":
        # settings 优先，其次 config 兜底
        try:
            city = app_settings.get_city() or ""
        except Exception:
            city = str(getattr(_config, "CITY", "")) or ""
    elif mode == "ip":
        # 预留：未来可以实现 IP 定位
        # 当前版本为了稳定性，不做真实网络调用，避免影响主流程
        if DEBUG:
            print("[Context] LOCATION_MODE='ip' 暂未实现，返回空城市")
        city = ""
    else:
        city = str(getattr(_config, "CITY", "")) or ""

    _city_cache["date"] = today
    _city_cache["value"] = city
    return city

