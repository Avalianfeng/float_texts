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
        self.setWindowTitle("欢迎")
        self.setFixedSize(420, 300)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("🌸 欢迎 🌸")
        title.setFont(QFont(FONT_NAME, 20))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 说明文本
        text = QTextEdit()
        text.setReadOnly(True)
        text.setFont(QFont(FONT_NAME, 12))
        text.setText(
            "For you ,翁小小 \n\n"
            "这是一个简单的桌面提醒工具。\n\n"
            "点击“开始”后，桌面上会显示浮动文本。\n\n"
            "关闭控制台窗口即可退出程序。\n\n"
            "\t\t\t from 策月帘风"
        )
        # 开始按钮
        start_btn = QPushButton("开启浮动文本")
        start_btn.setFont(QFont(FONT_NAME, 12))
        start_btn.clicked.connect(self.start)
        
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(start_btn)
    
    def start(self):
        """开始应用"""
        self.close()
        self.on_start()
