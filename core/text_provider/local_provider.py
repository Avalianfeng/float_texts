"""
本地文本提供者

从 data/texts.txt 或默认列表中读取文本
"""

from __future__ import annotations

import random
from typing import List

from .base import BaseTextProvider
from utils.text_loader import load_texts


class LocalTextProvider(BaseTextProvider):
    """本地文件文本提供者"""

    def __init__(self) -> None:
        super().__init__()
        self._texts: List[str] = []
        self._index: int = 0

    def prepare(self) -> None:
        """同步读取本地文本"""
        try:
            texts = load_texts()
            # 过滤空行
            self._texts = [t.strip() for t in texts if t and t.strip()]
            self._ready = bool(self._texts)
        except Exception as e:
            print(f"本地文本加载失败: {e}")
            self._texts = []
            self._ready = False

    def get_next_text(self) -> str:
        """随机返回一条文本"""
        if not self._texts:
            return ""
        return random.choice(self._texts)

