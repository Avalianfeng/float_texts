"""
主题工具模块
处理主题相关的逻辑
"""
import datetime
from config import COLOR_THEMES, NIGHT_THEMES


def get_theme():
    """
    根据当前时间返回合适的主题
    夜间模式：19:00 - 7:00
    """
    hour = datetime.datetime.now().hour
    if 19 <= hour or hour < 7:
        return NIGHT_THEMES
    else:
        return COLOR_THEMES
