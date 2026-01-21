"""
主程序入口
"""
import sys
import os
import warnings

# 抑制 libpng 的 ICC profile 警告（不影响功能）
os.environ.setdefault("QT_LOGGING_RULES", "*.debug=false")
warnings.filterwarnings("ignore", category=UserWarning, message=".*iCCP.*")

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from core.spawner import FloatSpawner
from core.app_controller import AppController
from ui.tray import TrayIcon


def main():
    """主函数"""
    # 创建 QApplication
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭所有窗口时不退出（因为有托盘）
    
    # 创建 Spawner
    spawner = FloatSpawner()
    
    # 创建 Controller
    controller = AppController(spawner=spawner)
    
    # 创建并显示托盘图标
    tray = TrayIcon(controller)
    
    # 检查系统托盘是否可用
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("错误: 系统不支持系统托盘")
        print("程序无法运行")
        return 1
    
    # 运行应用
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
