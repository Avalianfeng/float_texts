"""
主程序入口
"""
import sys
from PyQt6.QtWidgets import QApplication
from ui.start_dialog import StartDialog
from ui.tray import TrayIcon
from core.spawner import FloatSpawner
from core.idle_detector import IdleDetector
from core.hotkey import HotkeyManager


class FloatWordsApp:
    """漂浮文字应用主类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.spawner = FloatSpawner()
        self.tray = None
        self.idle_detector = None
        self.hotkey_manager = None
    
    def setup_tray(self):
        """设置系统托盘"""
        self.tray = TrayIcon(
            app=self.app,
            pause_callback=self.on_pause_changed,
            exit_callback=self.app.quit
        )
    
    def setup_hotkey(self):
        """设置全局热键"""
        self.hotkey_manager = HotkeyManager(exit_callback=self.app.quit)
        self.hotkey_manager.start()
    
    def setup_idle_detector(self):
        """设置空闲检测"""
        self.idle_detector = IdleDetector(on_idle_change=self.on_idle_changed)
        self.idle_detector.start()
    
    def on_pause_changed(self, paused):
        """暂停状态改变回调"""
        self.spawner.set_paused(paused)
    
    def on_idle_changed(self, is_idle):
        """空闲状态改变回调"""
        # 空闲时允许生成，活动时暂停生成
        self.spawner.set_paused(not is_idle)
    
    def start(self):
        """启动应用"""
        self.setup_tray()
        self.setup_hotkey()
        self.setup_idle_detector()
        
        # 显示启动对话框
        def on_start():
            self.spawner.start()
        
        start_dialog = StartDialog(on_start)
        start_dialog.show()
        
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = FloatWordsApp()
    app.start()
