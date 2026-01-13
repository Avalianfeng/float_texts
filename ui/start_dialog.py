"""
启动对话框组件
"""
from PyQt6.QtWidgets import QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config import FONT_NAME


class StartDialog(QWidget):
    """启动欢迎对话框"""
    
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("Welcome")
        self.setFixedSize(420, 300)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("🌸 Welcome 🌸")
        title.setFont(QFont(FONT_NAME, 20))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 说明文本
        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(QFont(FONT_NAME, 12))
        text.setText(
            "This is a gentle desktop companion tool.\n\n"
            "它会在你忙碌或安静的时候，\n"
            "轻轻出现一些话。\n\n"
            "你可以随时按 Alt + S 退出。\n\n"
            "希望它不会打扰你。"
        )
        
        # 开始按钮
        start_btn = QPushButton("开始")
        start_btn.setFont(QFont(FONT_NAME, 12))
        start_btn.clicked.connect(self.start)
        
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(start_btn)
    
    def start(self):
        """开始应用"""
        self.close()
        self.on_start()
