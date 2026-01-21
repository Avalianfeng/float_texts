"""
文字生成调度器
只负责定时发出生成请求，不管理窗口
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from config import SPAWN_INTERVAL


class FloatSpawner(QObject):
    """漂浮文字调度器 - 纯定时器，只负责发出生成请求"""
    
    # 生成请求信号
    spawnRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timeout)
        self.timer.setSingleShot(False)  # 重复定时器
    
    def start(self):
        """启动定时器"""
        if not self.timer.isActive():
            self.timer.start(SPAWN_INTERVAL)
    
    def stop(self):
        """停止定时器"""
        if self.timer.isActive():
            self.timer.stop()
    
    def _on_timeout(self):
        """定时器超时回调 - 只发出信号，不做其他事"""
        self.spawnRequested.emit()
