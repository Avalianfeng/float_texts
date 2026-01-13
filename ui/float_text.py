"""
漂浮文字窗口组件
"""
import random
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QApplication
from config import DECOR_ICONS, FONT_NAME, FONT_SIZE, LIFETIME, FLOAT_SPEED
from utils.theme import get_theme


class FloatText(QWidget):
    """漂浮文字窗口"""
    
    def __init__(self, text):
        super().__init__()
        self.setup_window()
        self.setup_label(text)
        self.setup_icon()
        self.setup_shadow()
        self.setup_position()
        self.setup_animation()
        self.show()
    
    def setup_window(self):
        """设置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def setup_label(self, text):
        """设置文字标签"""
        self.label = QLabel(text, self)
        self.label.setFont(QFont(FONT_NAME, FONT_SIZE))
        text_color, bg_color = random.choice(get_theme())
        self.label.setStyleSheet(f"""
            color: {text_color};
            background-color: {bg_color};
            border-radius: 12px;
            padding: 10px;
        """)
        self.label.adjustSize()
        self.resize(self.label.size())
    
    def setup_icon(self):
        """设置装饰图标"""
        icon = random.choice(DECOR_ICONS)
        self.icon_label = QLabel(icon, self)
        self.icon_label.setFont(QFont(FONT_NAME, 12))
        self.icon_label.setStyleSheet("background: transparent;")
        self.icon_label.adjustSize()
        icon_x = self.width() - self.icon_label.width() + 2
        icon_y = -4
        self.icon_label.move(icon_x, icon_y)
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
    def setup_shadow(self):
        """设置阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.label.setGraphicsEffect(shadow)
    
    def setup_position(self):
        """设置初始位置"""
        screen = QApplication.primaryScreen().availableGeometry()
        sw, sh = screen.width(), screen.height()
        w, h = self.width(), self.height()
        x_min = int(sw * 0.1)
        x_max = max(x_min, sw - w - 20)
        y_min = int(sh * 0.55)
        y_max = max(y_min, sh - h - 20)
        self.move(random.randint(x_min, x_max), random.randint(y_min, y_max))
    
    def setup_animation(self):
        """设置动画效果"""
        # 淡入动画
        self.anim_in = QPropertyAnimation(self, b"windowOpacity")
        self.anim_in.setDuration(600)
        self.anim_in.setStartValue(0)
        self.anim_in.setEndValue(1)
        self.anim_in.start()
        
        # 漂浮速度
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(0.3, 0.6)
        
        # 漂浮定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.float_up)
        self.timer.start(FLOAT_SPEED)
        
        # 淡出定时器
        QTimer.singleShot(LIFETIME, self.fade_out)
    
    def float_up(self):
        """漂浮动画"""
        self.vx += random.uniform(-0.05, 0.05)
        self.vx = max(-0.6, min(0.6, self.vx))
        self.move(int(self.x() + self.vx), int(self.y() - self.vy))
    
    def fade_out(self):
        """淡出动画"""
        self.timer.stop()
        self.anim_out = QPropertyAnimation(self, b"windowOpacity")
        self.anim_out.setDuration(800)
        self.anim_out.setStartValue(1)
        self.anim_out.setEndValue(0)
        self.anim_out.finished.connect(self.close)
        self.anim_out.start()
