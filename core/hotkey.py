"""
全局热键处理
"""
import threading
import keyboard
from config import HOTKEY_EXIT


class HotkeyManager:
    """全局热键管理器"""
    
    def __init__(self, exit_callback):
        """
        初始化热键管理器
        :param exit_callback: 退出回调函数
        """
        self.exit_callback = exit_callback
        self.thread = None
    
    def start(self):
        """启动热键监听"""
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
    
    def _listen_loop(self):
        """热键监听循环"""
        keyboard.add_hotkey(HOTKEY_EXIT, self.exit_callback)
        keyboard.wait()
