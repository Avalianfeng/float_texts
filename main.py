"""
主程序入口
"""
import sys
import atexit
import signal
from PyQt6.QtWidgets import QApplication
from ui.start_dialog import StartDialog
from core.spawner import FloatSpawner


class FloatWordsApp:
    """漂浮文字应用主类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.spawner = FloatSpawner()
        # 注册退出时的清理函数
        atexit.register(self.cleanup)
        # 注册信号处理（用于处理控制台关闭）
        if sys.platform == 'win32':
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """清理资源"""
        # 关闭所有漂浮文字窗口
        self.spawner.close_all()
    
    def start(self):
        """启动应用"""
        # 显示启动对话框
        def on_start():
            # 启动生成器
            self.spawner.start()
        
        start_dialog = StartDialog(on_start)
        start_dialog.show()
        
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = FloatWordsApp()
    app.start()
