"""
全局热键处理
"""
import threading
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
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
        self.keyboard_available = KEYBOARD_AVAILABLE
    
    def start(self):
        """启动热键监听"""
        if not self.keyboard_available:
            print("警告: keyboard库不可用，全局热键功能将不可用")
            return
        
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
    
    def _listen_loop(self):
        """热键监听循环"""
        try:
            keyboard.add_hotkey(HOTKEY_EXIT, self.exit_callback)
            keyboard.wait()
        except Exception as e:
            print(f"热键设置失败: {e}")
