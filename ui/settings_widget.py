"""
设置组件（QWidget）

从 SettingsDialog 拆分出来，可嵌入到 Tab 或其他容器中
"""

from __future__ import annotations

import os
from typing import List

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QPlainTextEdit,
    QPushButton,
    QMessageBox,
    QGroupBox,
)

from core import settings as app_settings


class SettingsWidget(QWidget):
    """设置组件，可嵌入到 Tab 或其他容器"""
    
    settingsChanged = pyqtSignal(list)  # changed_keys: list[str]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        root = QVBoxLayout(self)
        root.setSpacing(12)
        
        # 环境变量提示
        env_key = (os.getenv("DEEPSEEK_API_KEY", "") or "").strip()
        self.env_hint = QLabel("")
        self.env_hint.setWordWrap(True)
        self.env_hint.setStyleSheet("color: #666; padding: 8px; background: #f5f5f5; border-radius: 4px;")
        if env_key:
            self.env_hint.setText("ℹ️ 检测到环境变量 `DEEPSEEK_API_KEY`：实际请求会优先使用环境变量。")
        else:
            self.env_hint.setText("ℹ️ 未检测到环境变量 `DEEPSEEK_API_KEY`：将使用本窗口保存的 Key。")
        root.addWidget(self.env_hint)

        # 基础设置组
        basic_group = QGroupBox("基础设置")
        basic_form = QFormLayout()
        basic_group.setLayout(basic_form)
        
        # 文本来源
        self.text_source = QComboBox()
        self.text_source.addItems(["auto", "local", "ai"])
        basic_form.addRow(QLabel("文本来源"), self.text_source)
        
        # 漂浮数量
        self.float_density = QComboBox()
        self.float_density.addItems(["超多", "多", "普通", "少"])
        basic_form.addRow(QLabel("漂浮数量"), self.float_density)
        
        # 漂浮速度
        self.float_speed = QComboBox()
        self.float_speed.addItems(["快", "正常", "慢"])
        basic_form.addRow(QLabel("漂浮速度"), self.float_speed)
        
        # 仅空闲时显示
        self.idle_only = QCheckBox("仅空闲时显示")
        self.idle_only.toggled.connect(self._on_idle_only_toggled)
        basic_form.addRow(QLabel("空闲检测"), self.idle_only)
        
        # 空闲阈值
        self.idle_threshold = QSpinBox()
        self.idle_threshold.setRange(0, 3600)
        self.idle_threshold.setSuffix(" 秒")
        basic_form.addRow(QLabel("空闲阈值"), self.idle_threshold)
        
        root.addWidget(basic_group)

        # AI 设置组
        ai_group = QGroupBox("AI 设置")
        ai_form = QFormLayout()
        ai_group.setLayout(ai_form)
        
        # AI enabled
        self.ai_enabled = QCheckBox("启用 AI（DeepSeek）")
        self.ai_enabled.toggled.connect(self._on_ai_enabled_toggled)
        ai_form.addRow(QLabel("AI"), self.ai_enabled)
        
        # text source（移到基础组了，这里不需要）
        
        # api key
        api_row = QHBoxLayout()
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("DeepSeek API Key（将保存到本机设置）")
        self.toggle_key_btn = QPushButton("显示")
        self.toggle_key_btn.setFixedWidth(64)
        self.toggle_key_btn.clicked.connect(self._toggle_key_visibility)
        self.clear_key_btn = QPushButton("清空")
        self.clear_key_btn.setFixedWidth(64)
        self.clear_key_btn.clicked.connect(self._clear_key)
        api_row.addWidget(self.api_key)
        api_row.addWidget(self.toggle_key_btn)
        api_row.addWidget(self.clear_key_btn)
        ai_form.addRow(QLabel("DeepSeek Key"), api_row)
        
        # salutation
        self.salutation = QLineEdit()
        self.salutation.setPlaceholderText("例如：小王、阿哲（可为空）")
        ai_form.addRow(QLabel("称呼"), self.salutation)
        
        # user custom prompt
        self.user_prompt = QPlainTextEdit()
        self.user_prompt.setPlaceholderText(
            "用一句或几句自然语言描述你想要的风格或主题，例如：\n"
            "“偏学习与专注提醒，少鸡汤。”\n"
            "“更偏治愈、轻松，适合晚上。”\n"
            "“多一些喝水、拉伸、护眼的温柔提醒。”\n"
            "建议长度：20～200 字；不要写太长的段落。\n"
            "不要包含：网址、广告、敏感内容、极端/攻击性内容。"
        )
        self.user_prompt.setMaximumBlockCount(20)
        self.user_prompt.setFixedHeight(100)
        ai_form.addRow(QLabel("自定义提示词"), self.user_prompt)
        
        root.addWidget(ai_group)

        # 上下文设置组
        context_group = QGroupBox("上下文设置")
        context_form = QFormLayout()
        context_group.setLayout(context_form)
        
        # city
        self.city = QLineEdit()
        self.city.setPlaceholderText("可为空：不提供城市上下文")
        self.city.textChanged.connect(self._on_city_changed)
        context_form.addRow(QLabel("城市 City"), self.city)
        
        # weather enabled
        self.weather_enabled = QCheckBox("启用天气上下文（Open-Meteo，无需 API Key）")
        self.weather_enabled.toggled.connect(self._on_weather_enabled_toggled)
        context_form.addRow(QLabel("天气"), self.weather_enabled)
        
        self.weather_hint = QLabel("")
        self.weather_hint.setWordWrap(True)
        self.weather_hint.setStyleSheet("color: #d97706; font-size: 11px;")
        context_form.addRow("", self.weather_hint)
        
        root.addWidget(context_group)
        
        root.addStretch()

        # 保存按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.save_btn = QPushButton("保存设置")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self.save_btn)
        root.addLayout(btn_row)

        self._load()
        self._update_dynamic_states()

    def _on_ai_enabled_toggled(self, checked: bool):
        """AI 启用状态改变时，动态启用/禁用相关控件"""
        self.api_key.setEnabled(checked)
        self.toggle_key_btn.setEnabled(checked)
        self.clear_key_btn.setEnabled(checked)
        self.salutation.setEnabled(checked)
        self.user_prompt.setEnabled(checked)

    def _on_idle_only_toggled(self, checked: bool):
        """空闲检测开关改变时，动态启用/禁用阈值"""
        self.idle_threshold.setEnabled(checked)

    def _on_weather_enabled_toggled(self, checked: bool):
        """天气开关改变时，检查城市是否为空"""
        self._update_weather_hint()

    def _on_city_changed(self, text: str):
        """城市输入改变时，更新天气提示"""
        self._update_weather_hint()

    def _update_weather_hint(self):
        """更新天气提示信息"""
        if self.weather_enabled.isChecked():
            city = (self.city.text() or "").strip()
            if not city:
                self.weather_hint.setText("⚠️ 城市为空，天气将无法获取")
            else:
                self.weather_hint.setText("")
        else:
            self.weather_hint.setText("")

    def _update_dynamic_states(self):
        """更新动态状态（启用/禁用）"""
        self._on_ai_enabled_toggled(self.ai_enabled.isChecked())
        self._on_idle_only_toggled(self.idle_only.isChecked())
        self._update_weather_hint()

    def _toggle_key_visibility(self):
        """切换 Key 显示/隐藏"""
        if self.api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("隐藏")
        else:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("显示")

    def _clear_key(self):
        """清空 API Key"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空 API Key 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.api_key.clear()

    def _load(self):
        """加载设置"""
        self.ai_enabled.setChecked(app_settings.get_ai_enabled())
        self.text_source.setCurrentText(app_settings.get_text_source())
        self.api_key.setText(app_settings.get_deepseek_api_key())
        self.city.setText(app_settings.get_city())
        self.weather_enabled.setChecked(app_settings.get_weather_enabled())
        self.idle_only.setChecked(app_settings.get_idle_only())
        self.idle_threshold.setValue(app_settings.get_idle_threshold_seconds())
        self.float_density.setCurrentText(app_settings.get_float_density_label())
        self.float_speed.setCurrentText(app_settings.get_float_speed_label())
        self.salutation.setText(app_settings.get_salutation())
        self.user_prompt.setPlainText(app_settings.get_user_custom_prompt())

    def _on_save(self):
        """保存设置"""
        changed: List[str] = []

        # AI enabled
        if app_settings.get_ai_enabled() != self.ai_enabled.isChecked():
            app_settings.set_ai_enabled(self.ai_enabled.isChecked())
            changed.append(app_settings.Keys.AI_ENABLED)

        # text source
        src = self.text_source.currentText().strip().lower()
        if app_settings.get_text_source() != src:
            app_settings.set_text_source(src)
            changed.append(app_settings.Keys.AI_TEXT_SOURCE)

        # api key
        key = (self.api_key.text() or "").strip()
        if app_settings.get_deepseek_api_key() != key:
            app_settings.set_deepseek_api_key(key)
            changed.append(app_settings.Keys.AI_DEEPSEEK_API_KEY)

        # city
        city = (self.city.text() or "").strip()
        if app_settings.get_city() != city:
            app_settings.set_city(city)
            changed.append(app_settings.Keys.CONTEXT_CITY)

        # weather enabled
        if app_settings.get_weather_enabled() != self.weather_enabled.isChecked():
            app_settings.set_weather_enabled(self.weather_enabled.isChecked())
            changed.append(app_settings.Keys.CONTEXT_WEATHER_ENABLED)

        # idle only
        if app_settings.get_idle_only() != self.idle_only.isChecked():
            app_settings.set_idle_only(self.idle_only.isChecked())
            changed.append(app_settings.Keys.IDLE_ENABLED)

        # idle threshold
        th = int(self.idle_threshold.value())
        if app_settings.get_idle_threshold_seconds() != th:
            app_settings.set_idle_threshold_seconds(th)
            changed.append(app_settings.Keys.IDLE_THRESHOLD_SECONDS)

        # float density
        density = self.float_density.currentText().strip()
        if app_settings.get_float_density_label() != density:
            app_settings.set_float_density_label(density)
            changed.append(app_settings.Keys.UI_FLOAT_DENSITY)

        # float speed
        speed = self.float_speed.currentText().strip()
        if app_settings.get_float_speed_label() != speed:
            app_settings.set_float_speed_label(speed)
            changed.append(app_settings.Keys.UI_FLOAT_SPEED)

        # salutation
        salutation = (self.salutation.text() or "").strip()
        if app_settings.get_salutation() != salutation:
            app_settings.set_salutation(salutation)
            changed.append(app_settings.Keys.PROMPT_SALUTATION)

        # user custom prompt
        user_prompt = (self.user_prompt.toPlainText() or "").strip()
        if app_settings.get_user_custom_prompt() != user_prompt:
            app_settings.set_user_custom_prompt(user_prompt)
            changed.append(app_settings.Keys.PROMPT_USER_HINT)

        # 校验提示
        env_key = (os.getenv("DEEPSEEK_API_KEY", "") or "").strip()
        if self.ai_enabled.isChecked() and src in ("auto", "ai") and (not env_key) and (not key):
            QMessageBox.information(
                self,
                "提示",
                "你启用了 AI，但没有配置 DeepSeek Key（环境变量与本机设置都为空）。\n"
                "保存是允许的，但 AI 可能无法生成文本。",
            )

        if changed:
            # 检查是否需要刷新 AI 文本
            needs_refresh = any(
                k in changed
                for k in [
                    app_settings.Keys.CONTEXT_CITY,
                    app_settings.Keys.CONTEXT_WEATHER_ENABLED,
                    app_settings.Keys.PROMPT_SALUTATION,
                    app_settings.Keys.PROMPT_USER_HINT,
                ]
            )
            
            if needs_refresh:
                QMessageBox.information(
                    self,
                    "提示",
                    "设置已保存。\n"
                    "部分更改（城市/天气/称呼/提示词）需要刷新今日 AI 文本才能生效。\n"
                    "请在首页点击“刷新今日 AI 文本”按钮。",
                )
            else:
                QMessageBox.information(self, "提示", "设置已保存。")
            
            self.settingsChanged.emit(changed)
