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
    CONTEXT_WEATHER_ENABLED = "context/weather_enabled"
    IDLE_ENABLED = "idle/enabled"
    IDLE_THRESHOLD_SECONDS = "idle/threshold_seconds"
    UI_FLOAT_DENSITY = "ui/float_density"  # 超多/多/普通/少
    UI_FLOAT_SPEED = "ui/float_speed"  # 快/正常/慢
    UI_SHOW_PANEL_ON_STARTUP = "ui/show_panel_on_startup"  # 启动时显示控制面板
    PROMPT_SALUTATION = "prompt/salutation"
    PROMPT_USER_HINT = "prompt/user_hint"


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


def get_weather_enabled() -> bool:
    """是否启用天气上下文（Open-Meteo，无需 API Key）"""
    return get_bool(Keys.CONTEXT_WEATHER_ENABLED, bool(getattr(_config, "WEATHER_ENABLED", False)))


def set_weather_enabled(v: bool) -> None:
    set_value(Keys.CONTEXT_WEATHER_ENABLED, bool(v))


def get_idle_only() -> bool:
    return get_bool(Keys.IDLE_ENABLED, bool(getattr(_config, "IDLE_ONLY", True)))


def set_idle_only(v: bool) -> None:
    set_value(Keys.IDLE_ENABLED, bool(v))


def get_idle_threshold_seconds() -> int:
    v = get_int(Keys.IDLE_THRESHOLD_SECONDS, int(getattr(_config, "IDLE_THRESHOLD_SECONDS", 30)))
    return max(0, v)


def set_idle_threshold_seconds(v: int) -> None:
    set_value(Keys.IDLE_THRESHOLD_SECONDS, int(v))


# -------- UI 档位：数量/速度 --------


_DENSITY_TO_MAX_FLOATS = {
    "超多": 30,
    "多": 15,
    "普通": 8,
    "少": 3,
}

_SPEED_TO_MS = {
    "快": 25,
    "正常": 40,
    "慢": 60,
}


def get_float_density_label() -> str:
    """漂浮数量档位（中文）"""
    default_max = int(getattr(_config, "MAX_FLOATS", 6))
    # 用默认 max_floats 推断一个最接近的档位
    if default_max >= 15:
        default_label = "超多"
    elif default_max >= 8:
        default_label = "多"
    elif default_max >= 4:
        default_label = "普通"
    else:
        default_label = "少"

    v = get_str(Keys.UI_FLOAT_DENSITY, default_label).strip()
    return v if v in _DENSITY_TO_MAX_FLOATS else default_label


def set_float_density_label(v: str) -> None:
    set_value(Keys.UI_FLOAT_DENSITY, (v or "").strip())


def get_max_floats() -> int:
    """将档位映射为窗口上限"""
    label = get_float_density_label()
    return int(_DENSITY_TO_MAX_FLOATS.get(label, int(getattr(_config, "MAX_FLOATS", 6))))


def get_float_speed_label() -> str:
    """漂浮速度档位（中文）"""
    default_ms = int(getattr(_config, "FLOAT_SPEED", 40))
    if default_ms <= 30:
        default_label = "快"
    elif default_ms <= 50:
        default_label = "正常"
    else:
        default_label = "慢"

    v = get_str(Keys.UI_FLOAT_SPEED, default_label).strip()
    return v if v in _SPEED_TO_MS else default_label


def set_float_speed_label(v: str) -> None:
    set_value(Keys.UI_FLOAT_SPEED, (v or "").strip())


def get_float_speed_ms() -> int:
    """将档位映射为 QTimer 间隔（ms）"""
    label = get_float_speed_label()
    return int(_SPEED_TO_MS.get(label, int(getattr(_config, "FLOAT_SPEED", 40))))


def get_show_panel_on_startup() -> bool:
    """是否在启动时显示控制面板"""
    return get_bool(Keys.UI_SHOW_PANEL_ON_STARTUP, True)  # 默认 True


def set_show_panel_on_startup(v: bool) -> None:
    """设置是否在启动时显示控制面板"""
    set_value(Keys.UI_SHOW_PANEL_ON_STARTUP, bool(v))


# -------- Prompt 相关：称呼 & 自定义提示词 --------


def get_salutation() -> str:
    """称呼，如“小王”、“阿哲”等，可为空"""
    return get_str(Keys.PROMPT_SALUTATION, "").strip()


def set_salutation(v: str) -> None:
    set_value(Keys.PROMPT_SALUTATION, (v or "").strip())


def get_user_custom_prompt() -> str:
    """用户自定义提示词，可多句自然语言"""
    return get_str(Keys.PROMPT_USER_HINT, "").strip()


def set_user_custom_prompt(v: str) -> None:
    set_value(Keys.PROMPT_USER_HINT, (v or "").strip())

