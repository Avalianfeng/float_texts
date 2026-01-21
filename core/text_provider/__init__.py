"""
文本提供者模块

封装本地与 AI 文本来源的统一接口
"""

from .base import BaseTextProvider
from .local_provider import LocalTextProvider

__all__ = [
    "BaseTextProvider",
    "LocalTextProvider",
]

