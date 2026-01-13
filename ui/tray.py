"""
系统托盘组件
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from config import ICON_FILE


class TrayIcon:
    """系统托盘图标管理"""
    
    def __init__(self, app, pause_callback, exit_callback):
        self.app = app
        self.pause_callback = pause_callback
        self.exit_callback = exit_callback
        self.paused = False
        self.setup_tray()
    
    def setup_tray(self):
        """设置系统托盘"""
        self.tray = QSystemTrayIcon()
        try:
            self.tray.setIcon(QIcon(ICON_FILE))
        except:
            pass  # 如果图标文件不存在，使用默认图标
        self.tray.setVisible(True)
        
        menu = QMenu()
        
        # 暂停/继续菜单
        self.pause_action = QAction("暂停")
        self.pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(self.pause_action)
        
        # 退出菜单
        exit_action = QAction("退出")
        exit_action.triggered.connect(self.exit_callback)
        menu.addAction(exit_action)
        
        self.tray.setContextMenu(menu)
    
    def toggle_pause(self):
        """切换暂停状态"""
        self.paused = not self.paused
        self.pause_action.setText("继续" if self.paused else "暂停")
        if self.pause_callback:
            self.pause_callback(self.paused)
    
    def get_paused(self):
        """获取暂停状态"""
        return self.paused
