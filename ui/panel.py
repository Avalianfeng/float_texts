"""
控制面板（统一入口窗口）

包含两个 Tab：
- Home：首页（欢迎、快速操作、状态）
- Settings：设置页
"""

from __future__ import annotations

import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QCheckBox,
    QWidget,
    QFrame,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QPixmap, QFont

from ui.settings_widget import SettingsWidget
from core import settings as app_settings
from utils.resources import get_resource_path, get_icon_path


class HomeTab(QWidget):
    """首页 Tab"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        root = QVBoxLayout(self)
        root.setSpacing(16)
        root.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QVBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 图标
        icon_path, _ = get_icon_path()
        icon_label = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon_label)
        
        # 应用名称
        name_label = QLabel("Float Words")
        name_font = QFont()
        name_font.setPointSize(20)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(name_label)
        
        # 副标题
        subtitle_label = QLabel("漂浮文字桌面伴侣")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #666; font-size: 12px;")
        header.addWidget(subtitle_label)
        
        root.addLayout(header)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        root.addWidget(line)

        # Quick Actions
        actions_label = QLabel("快速操作")
        actions_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        root.addWidget(actions_label)
        
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(8)
        
        # 开始/暂停按钮
        self.start_pause_btn = QPushButton("开始显示")
        self.start_pause_btn.setMinimumHeight(40)
        self.start_pause_btn.setStyleSheet("font-size: 14px;")
        self.start_pause_btn.clicked.connect(self._on_start_pause)
        actions_layout.addWidget(self.start_pause_btn)
        
        # 刷新 AI 文本按钮
        self.refresh_ai_btn = QPushButton("刷新今日 AI 文本")
        self.refresh_ai_btn.setMinimumHeight(36)
        self.refresh_ai_btn.clicked.connect(self._on_refresh_ai)
        actions_layout.addWidget(self.refresh_ai_btn)
        
        root.addLayout(actions_layout)

        # 状态信息
        status_label = QLabel("当前状态")
        status_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 12px;")
        root.addWidget(status_label)
        
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("background: #f5f5f5; border-radius: 4px; padding: 12px;")
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setSpacing(6)
        
        self.text_source_label = QLabel()
        self.ai_status_label = QLabel()
        self.city_weather_label = QLabel()
        self.idle_status_label = QLabel()
        
        status_layout.addWidget(self.text_source_label)
        status_layout.addWidget(self.ai_status_label)
        status_layout.addWidget(self.city_weather_label)
        status_layout.addWidget(self.idle_status_label)
        
        root.addWidget(self.status_frame)

        root.addStretch()

        # 底部提示
        hint_label = QLabel("💡 提示：关闭此窗口不会退出程序，程序会最小化到系统托盘")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #999; font-size: 11px; padding: 8px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(hint_label)

        # 连接信号更新状态
        if self.controller:
            self.controller.stateChanged.connect(self._update_status)
            self.controller.providerChanged.connect(self._update_status)
            self.controller.aiPreparingChanged.connect(self._update_status)
        
        self._update_status()

    def _on_start_pause(self):
        """开始/暂停按钮点击"""
        if self.controller:
            if self.controller.running:
                self.controller.pause()
            else:
                self.controller.start()

    def _on_refresh_ai(self):
        """刷新 AI 文本"""
        if self.controller:
            self.controller.refresh_today_ai()
            QMessageBox.information(self, "提示", "正在刷新今日 AI 文本，请稍候...")

    def _update_status(self):
        """更新状态显示"""
        if not self.controller:
            return
        
        # 更新开始/暂停按钮
        if self.controller.running:
            self.start_pause_btn.setText("暂停显示")
            self.start_pause_btn.setStyleSheet("font-size: 14px; background: #ff6b6b; color: white;")
        else:
            self.start_pause_btn.setText("开始显示")
            self.start_pause_btn.setStyleSheet("font-size: 14px; background: #51cf66; color: white;")
        
        # 文本来源
        text_source = app_settings.get_text_source()
        self.text_source_label.setText(f"📝 文本来源: {text_source}")
        
        # AI 状态
        ai_enabled = app_settings.get_ai_enabled()
        env_key = (os.getenv("DEEPSEEK_API_KEY", "") or "").strip()
        settings_key = app_settings.get_deepseek_api_key()
        has_key = bool(env_key or settings_key)
        
        if ai_enabled:
            if has_key:
                # 检查 AI 是否正在准备中
                preparing = False
                if self.controller and hasattr(self.controller, 'ai_provider'):
                    provider = self.controller.ai_provider
                    if provider and hasattr(provider, 'preparing'):
                        preparing = provider.preparing
                
                if preparing:
                    self.ai_status_label.setText("🤖 AI: 已启用，正在准备中...")
                else:
                    self.ai_status_label.setText("🤖 AI: 已启用，Key 已配置")
            else:
                self.ai_status_label.setText("🤖 AI: 已启用，但 Key 未配置")
        else:
            self.ai_status_label.setText("🤖 AI: 未启用")
        
        # 城市/天气
        city = app_settings.get_city()
        weather_enabled = app_settings.get_weather_enabled()
        if city:
            weather_text = "已启用" if weather_enabled else "未启用"
            self.city_weather_label.setText(f"🌍 城市: {city} | 天气: {weather_text}")
        else:
            self.city_weather_label.setText("🌍 城市: 未设置 | 天气: 未启用")
        
        # 空闲检测
        idle_only = app_settings.get_idle_only()
        idle_threshold = app_settings.get_idle_threshold_seconds()
        if idle_only:
            self.idle_status_label.setText(f"⏱️ 空闲检测: 已启用（阈值: {idle_threshold} 秒）")
        else:
            self.idle_status_label.setText("⏱️ 空闲检测: 未启用")


class ControlPanel(QDialog):
    """控制面板（统一入口窗口）"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # 设置窗口属性
        self.setWindowTitle("Float Words | 漂浮文字")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
        )
        
        # 设置窗口大小和缩放限制
        self.setMinimumSize(500, 600)
        self.setMaximumSize(1200, 1000)
        self.resize(600, 700)  # 设置初始大小
        
        # 设置图标（优先 .ico，Windows 任务栏显示更好）
        icon_path, fallback_path = get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        elif os.path.exists(fallback_path):
            self.setWindowIcon(QIcon(fallback_path))
        
        # 居中显示
        self._center_window()
        
        self._setup_ui()
        
        # 连接设置变更信号
        if self.settings_widget:
            self.settings_widget.settingsChanged.connect(self._on_settings_changed)
    
    def _center_window(self):
        """将窗口居中显示"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        window_rect = self.frameGeometry()
        center_point = screen.center()
        window_rect.moveCenter(center_point)
        self.move(window_rect.topLeft())

    def _setup_ui(self):
        """设置 UI"""
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Home Tab
        self.home_tab = HomeTab(self.controller, self)
        self.tabs.addTab(self.home_tab, "首页")
        
        # Settings Tab
        self.settings_widget = SettingsWidget(self)
        self.tabs.addTab(self.settings_widget, "设置")
        
        root.addWidget(self.tabs)

        # 底部：启动时显示复选框
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(12, 8, 12, 8)
        bottom_layout.addStretch(1)
        
        self.show_on_startup = QCheckBox("下次启动时显示此窗口")
        self.show_on_startup.setChecked(app_settings.get_show_panel_on_startup())
        self.show_on_startup.toggled.connect(self._on_show_on_startup_toggled)
        bottom_layout.addWidget(self.show_on_startup)
        
        root.addLayout(bottom_layout)

    def _on_show_on_startup_toggled(self, checked: bool):
        """启动时显示复选框改变"""
        app_settings.set_show_panel_on_startup(checked)

    def _on_settings_changed(self, changed_keys: list):
        """设置变更回调"""
        if self.controller:
            try:
                self.controller.apply_settings(changed_keys)
            except Exception as e:
                print(f"[Panel] 应用设置失败: {e}")
        
        # 更新首页状态
        if self.home_tab:
            self.home_tab._update_status()

    def closeEvent(self, event):
        """关闭事件：隐藏到托盘，不退出"""
        event.ignore()
        self.hide()
        
    def show_home(self):
        """显示并切换到首页"""
        # 确保窗口在屏幕可见区域内
        self._ensure_visible()
        self.show()
        self.activateWindow()
        self.raise_()
        self.tabs.setCurrentIndex(0)
        
    def show_settings(self):
        """显示并切换到设置页"""
        # 确保窗口在屏幕可见区域内
        self._ensure_visible()
        self.show()
        self.activateWindow()
        self.raise_()
        self.tabs.setCurrentIndex(1)
    
    def _ensure_visible(self):
        """确保窗口在屏幕可见区域内"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        window_rect = self.geometry()
        
        # 检查窗口是否完全在屏幕内
        if window_rect.left() < screen.left():
            window_rect.moveLeft(screen.left())
        if window_rect.top() < screen.top():
            window_rect.moveTop(screen.top())
        if window_rect.right() > screen.right():
            window_rect.moveRight(screen.right())
        if window_rect.bottom() > screen.bottom():
            window_rect.moveBottom(screen.bottom())
        
        # 如果窗口完全超出屏幕，则居中显示
        if (window_rect.right() < screen.left() or 
            window_rect.left() > screen.right() or
            window_rect.bottom() < screen.top() or
            window_rect.top() > screen.bottom()):
            self._center_window()
        else:
            self.setGeometry(window_rect)