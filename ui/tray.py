"""
系统托盘组件
"""
import os
import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt
from ui.settings_dialog import SettingsDialog
from core import settings as app_settings


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径
    支持开发环境和PyInstaller打包后的环境
    """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境，使用当前文件所在目录
        base_path = os.path.abspath(os.path.dirname(__file__))
        # 回到项目根目录
        base_path = os.path.dirname(base_path)
    
    return os.path.join(base_path, relative_path)


def create_default_icon():
    """创建默认图标"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    # 绘制一个简单的花朵图标
    painter.setBrush(QColor(255, 182, 193))  # 浅粉色
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(8, 8, 16, 16)
    painter.setBrush(QColor(255, 105, 180))  # 深粉色
    painter.drawEllipse(10, 10, 12, 12)
    painter.end()
    return QIcon(pixmap)


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标"""
    
    def __init__(self, controller):
        """
        初始化系统托盘
        
        :param controller: AppController 实例
        """
        super().__init__()
        self.controller = controller
        self._settings_dialog: SettingsDialog | None = None
        
        # 设置图标
        self._setup_icon()
        
        # 创建菜单
        self._setup_menu()
        
        # 连接状态改变信号
        self.controller.stateChanged.connect(self._on_state_changed)
        self.controller.providerChanged.connect(self._on_provider_changed)
        self.controller.aiPreparingChanged.connect(self._on_ai_preparing_changed)
        
        # 初始状态
        self._update_menu_state()
    
    def _setup_icon(self):
        """设置托盘图标"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("警告: 系统不支持系统托盘")
            return
        
        # 尝试加载图标文件
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            try:
                self.setIcon(QIcon(icon_path))
            except Exception as e:
                print(f"加载图标文件失败: {e}")
                self.setIcon(create_default_icon())
        else:
            # 使用默认图标
            self.setIcon(create_default_icon())
        
        self.setVisible(True)
    
    def _setup_menu(self):
        """设置托盘菜单"""
        menu = QMenu()
        
        # 开始菜单
        self.start_action = QAction("开始", self)
        self.start_action.triggered.connect(self.controller.start)
        menu.addAction(self.start_action)
        
        # 暂停菜单
        self.pause_action = QAction("暂停", self)
        self.pause_action.triggered.connect(self.controller.pause)
        menu.addAction(self.pause_action)
        
        # 分隔线
        menu.addSeparator()
        
        # 仅空闲时显示开关
        self.idle_only_action = QAction("仅空闲时显示", self)
        self.idle_only_action.setCheckable(True)
        self.idle_only_action.setChecked(bool(getattr(self.controller, "idle_only", False)))
        self.idle_only_action.triggered.connect(self._on_idle_only_toggled)
        menu.addAction(self.idle_only_action)

        # AI 文本开关（DeepSeek）
        self.ai_action = QAction("使用 AI 文本（DeepSeek）", self)
        self.ai_action.setCheckable(True)
        self.ai_action.setChecked(False)
        self.ai_action.triggered.connect(self._on_ai_toggled)
        menu.addAction(self.ai_action)

        # 刷新今日 AI 文本
        self.refresh_ai_action = QAction("刷新今日 AI 文本", self)
        self.refresh_ai_action.triggered.connect(self._on_refresh_ai)
        menu.addAction(self.refresh_ai_action)
        
        # 设置
        self.settings_action = QAction("设置…", self)
        self.settings_action.triggered.connect(self._open_settings)
        menu.addAction(self.settings_action)

        # 分隔线
        menu.addSeparator()
        
        # 退出菜单
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.controller.exit)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
    
    def _on_idle_only_toggled(self, checked: bool):
        """空闲显示开关切换"""
        self.controller.idle_only = checked
        # 写入 settings（可选但更符合“用户设置”预期）
        try:
            app_settings.set_idle_only(checked)
        except Exception:
            pass

    def _on_ai_toggled(self, checked: bool):
        """AI 文本开关"""
        self.controller.set_ai_enabled(checked)
        try:
            app_settings.set_ai_enabled(checked)
        except Exception:
            pass

    def _on_refresh_ai(self):
        """刷新今日 AI 文本"""
        self.controller.refresh_today_ai()

    def _open_settings(self):
        """打开设置窗口（单实例）"""
        if self._settings_dialog is None:
            self._settings_dialog = SettingsDialog()
            self._settings_dialog.settingsChanged.connect(self._on_settings_changed)

        # 阻塞式更符合设置窗口习惯
        self._settings_dialog.exec()

    def _on_settings_changed(self, changed_keys: list):
        """设置保存回调：让 controller 应用并提示必要的刷新"""
        try:
            self.controller.apply_settings(changed_keys)
        except Exception as e:
            print(f"[Settings] 应用设置失败: {e}")
    
    def _on_state_changed(self, running: bool):
        """状态改变回调"""
        self._update_menu_state()

    def _on_provider_changed(self, provider: str):
        """Provider 改变回调（local/ai）"""
        # 同步 AI 勾选状态
        if provider == "ai":
            self.ai_action.setChecked(True)
        elif provider == "local":
            self.ai_action.setChecked(False)

        self._update_menu_state()

    def _on_ai_preparing_changed(self, preparing: bool):
        """AI 准备状态变化：禁用刷新/避免重入"""
        self._update_menu_state()
    
    def _update_menu_state(self):
        """更新菜单状态"""
        running = self.controller.running
        
        # 根据运行状态更新菜单项
        self.start_action.setEnabled(not running)
        self.pause_action.setEnabled(running)

        # 刷新按钮：AI 勾选且不在 preparing 时才启用
        preparing = getattr(self.controller, "_ai_preparing", False)
        self.refresh_ai_action.setEnabled(self.ai_action.isChecked() and (not preparing))
        # AI 正在准备时，禁用勾选项防止连点
        self.ai_action.setEnabled(not preparing)
        
        # 更新菜单文本
        if running:
            self.pause_action.setText("暂停")
        else:
            self.start_action.setText("开始")
