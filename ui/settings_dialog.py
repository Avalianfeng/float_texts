"""
设置窗口（QDialog）

第一版目标：
- 允许用户在 UI 内配置：AI 开关、文本来源、DeepSeek API Key、城市、空闲检测开关/阈值
- 使用 QSettings 持久化，不写回 config.py
"""

from __future__ import annotations

import os
from typing import List

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QSpinBox,
    QPushButton,
    QMessageBox,
)

from core import settings as app_settings


class SettingsDialog(QDialog):
    settingsChanged = pyqtSignal(list)  # changed_keys: list[str]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(420)

        self._changed_keys: List[str] = []

        root = QVBoxLayout(self)
        form = QFormLayout()
        root.addLayout(form)

        # env key 提示
        env_key = (os.getenv("DEEPSEEK_API_KEY", "") or "").strip()
        self.env_hint = QLabel("")
        self.env_hint.setWordWrap(True)
        if env_key:
            self.env_hint.setText("检测到环境变量 `DEEPSEEK_API_KEY`：实际请求会优先使用环境变量。")
        else:
            self.env_hint.setText("未检测到环境变量 `DEEPSEEK_API_KEY`：将使用本窗口保存的 Key。")
        form.addRow(QLabel("提示"), self.env_hint)

        # AI enabled
        self.ai_enabled = QCheckBox("启用 AI（DeepSeek）")
        form.addRow(QLabel("AI"), self.ai_enabled)

        # text source
        self.text_source = QComboBox()
        self.text_source.addItems(["auto", "local", "ai"])
        form.addRow(QLabel("文本来源"), self.text_source)

        # api key
        api_row = QHBoxLayout()
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("DeepSeek API Key（将保存到本机设置）")
        self.toggle_key_btn = QPushButton("显示")
        self.toggle_key_btn.setFixedWidth(64)
        self.toggle_key_btn.clicked.connect(self._toggle_key_visibility)
        api_row.addWidget(self.api_key)
        api_row.addWidget(self.toggle_key_btn)
        form.addRow(QLabel("DeepSeek Key"), api_row)

        # city
        self.city = QLineEdit()
        self.city.setPlaceholderText("可为空：不提供城市上下文")
        form.addRow(QLabel("城市 City"), self.city)

        # idle only
        self.idle_only = QCheckBox("仅空闲时显示")
        form.addRow(QLabel("空闲检测"), self.idle_only)

        # idle threshold
        self.idle_threshold = QSpinBox()
        self.idle_threshold.setRange(0, 3600)
        self.idle_threshold.setSuffix(" 秒")
        form.addRow(QLabel("空闲阈值"), self.idle_threshold)

        # buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.cancel_btn)
        root.addLayout(btn_row)

        self._load()

    def _toggle_key_visibility(self):
        if self.api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("隐藏")
        else:
            self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("显示")

    def _load(self):
        self.ai_enabled.setChecked(app_settings.get_ai_enabled())
        self.text_source.setCurrentText(app_settings.get_text_source())
        self.api_key.setText(app_settings.get_deepseek_api_key())
        self.city.setText(app_settings.get_city())
        self.idle_only.setChecked(app_settings.get_idle_only())
        self.idle_threshold.setValue(app_settings.get_idle_threshold_seconds())

    def _on_save(self):
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

        # api key（允许为空）
        key = (self.api_key.text() or "").strip()
        if app_settings.get_deepseek_api_key() != key:
            app_settings.set_deepseek_api_key(key)
            changed.append(app_settings.Keys.AI_DEEPSEEK_API_KEY)

        # city
        city = (self.city.text() or "").strip()
        if app_settings.get_city() != city:
            app_settings.set_city(city)
            changed.append(app_settings.Keys.CONTEXT_CITY)

        # idle only
        if app_settings.get_idle_only() != self.idle_only.isChecked():
            app_settings.set_idle_only(self.idle_only.isChecked())
            changed.append(app_settings.Keys.IDLE_ENABLED)

        # idle threshold
        th = int(self.idle_threshold.value())
        if app_settings.get_idle_threshold_seconds() != th:
            app_settings.set_idle_threshold_seconds(th)
            changed.append(app_settings.Keys.IDLE_THRESHOLD_SECONDS)

        # 轻量校验提示：启用 AI 且使用 ai/auto 时，没有 key（env+settings 都为空）
        env_key = (os.getenv("DEEPSEEK_API_KEY", "") or "").strip()
        if self.ai_enabled.isChecked() and src in ("auto", "ai") and (not env_key) and (not key):
            QMessageBox.information(
                self,
                "提示",
                "你启用了 AI，但没有配置 DeepSeek Key（环境变量与本机设置都为空）。\n"
                "保存是允许的，但 AI 可能无法生成文本。",
            )

        if changed:
            self.settingsChanged.emit(changed)
        self.accept()

