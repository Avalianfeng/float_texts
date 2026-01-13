"""
文字生成器
管理漂浮文字的生成逻辑
"""
import random
from PyQt6.QtCore import QTimer
from ui.float_text import FloatText
from config import MAX_FLOATS, SPAWN_INTERVAL
from utils.text_loader import load_texts


class FloatSpawner:
    """漂浮文字生成器"""
    
    def __init__(self):
        self.active_floats = []
        self.paused = False
        self.texts = load_texts()
    
    def set_paused(self, paused):
        """设置暂停状态"""
        self.paused = paused
    
    def spawn_float(self):
        """生成一个漂浮文字"""
        if self.paused:
            QTimer.singleShot(SPAWN_INTERVAL, self.spawn_float)
            return
        
        # 清理不可见的窗口
        if len(self.active_floats) >= MAX_FLOATS:
            self.active_floats[:] = [f for f in self.active_floats if f.isVisible()]
        
        # 创建新的漂浮文字
        text = random.choice(self.texts)
        float_text = FloatText(text)
        self.active_floats.append(float_text)
        
        # 安排下一次生成
        QTimer.singleShot(SPAWN_INTERVAL, self.spawn_float)
    
    def start(self):
        """开始生成"""
        self.spawn_float()
    
    def close_all(self):
        """关闭所有漂浮文字窗口"""
        # 停止生成新文字
        self.paused = True
        
        # 关闭所有已显示的窗口
        for float_text in self.active_floats:
            try:
                if float_text.isVisible():
                    # 使用强制关闭，立即关闭窗口
                    if hasattr(float_text, 'force_close'):
                        float_text.force_close()
                    else:
                        float_text.close()
            except:
                pass
        self.active_floats.clear()
