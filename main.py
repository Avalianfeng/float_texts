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
from ui.panel import ControlPanel
from core import settings as app_settings


def set_windows_appusermodelid():
    """
    设置 Windows AppUserModelID
    
    用于解决任务栏图标显示和分组问题
    必须在创建任何窗口之前调用
    """
    if sys.platform.startswith("win"):
        try:
            import ctypes
            # 使用反向域名格式：Avalianfeng.FloatWords
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Avalianfeng.FloatWords")
        except Exception:
            # 如果设置失败，静默忽略（不影响功能）
            pass


def main():
    """主函数"""
    # 设置 Windows AppUserModelID（必须在创建 QApplication 之前或之后，但在创建窗口之前）
    set_windows_appusermodelid()
    
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
    
    # 创建控制面板
    panel = ControlPanel(controller)
    tray.set_panel(panel)  # 让托盘可以打开面板
    
    # 根据设置决定是否显示面板
    if app_settings.get_show_panel_on_startup():
        panel.show_home()
    
    # 运行应用
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
