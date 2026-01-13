"""
空闲检测器
检测用户是否处于空闲状态
"""
import time
import threading
import mouse
from config import IDLE_THRESHOLD


class IdleDetector:
    """空闲检测器"""
    
    def __init__(self, on_idle_change):
        """
        初始化空闲检测器
        :param on_idle_change: 回调函数，当空闲状态改变时调用 (is_idle: bool)
        """
        self.on_idle_change = on_idle_change
        self.last_time = time.time()
        self.last_pos = None
        self.is_idle = False
        self.running = True
        self.thread = None
    
    def start(self):
        """启动空闲检测"""
        self.thread = threading.Thread(target=self._detect_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """停止空闲检测"""
        self.running = False
    
    def _detect_loop(self):
        """检测循环"""
        while self.running:
            current_pos = mouse.get_position()
            
            # 检测鼠标移动或点击
            if current_pos != self.last_pos or mouse.is_pressed(button='left'):
                self.last_pos = current_pos
                self.last_time = time.time()
                
                # 如果之前是空闲状态，现在变为活动状态
                if self.is_idle:
                    self.is_idle = False
                    if self.on_idle_change:
                        self.on_idle_change(False)
            
            # 检测是否超过空闲阈值
            elif time.time() - self.last_time > IDLE_THRESHOLD:
                # 如果之前是活动状态，现在变为空闲状态
                if not self.is_idle:
                    self.is_idle = True
                    if self.on_idle_change:
                        self.on_idle_change(True)
            
            time.sleep(1)
