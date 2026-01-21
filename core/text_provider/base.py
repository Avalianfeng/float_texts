"""
文本提供者抽象基类

不同文本来源（本地文件、AI 等）都应实现相同接口：
- prepare(): 同步准备数据（读文件 / 读缓存等）
- is_ready(): 是否已经就绪，可以提供文本
- get_next_text(): 返回一条文本
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class BaseTextProvider(ABC):
    """文本提供者基类"""

    def __init__(self) -> None:
        self._ready: bool = False

    @abstractmethod
    def prepare(self) -> None:
        """同步准备数据（读文件 / 读缓存 / 调用接口等）"""
        ...

    def is_ready(self) -> bool:
        """是否已经就绪"""
        return self._ready

    @abstractmethod
    def get_next_text(self) -> str:
        """返回一条文本，如果没有可用文本应抛出异常或返回空字符串"""
        ...

