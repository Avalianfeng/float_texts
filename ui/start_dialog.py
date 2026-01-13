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
            "This is a simple desktop reminder tool.\n\n"
            "After clicking Start, floating text will be displayed on the desktop.\n\n"
            "Close the console window to exit the program."
        )
        # 开始按钮
        start_btn = QPushButton("Start Floating Text")
        start_btn.setFont(QFont(FONT_NAME, 12))
        start_btn.clicked.connect(self.start)
        
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(start_btn)
    
    def start(self):
        """开始应用"""
        self.close()
        self.on_start()
