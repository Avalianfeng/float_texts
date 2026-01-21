"""
活动监控器
检测用户空闲时间（鼠标/键盘活动）
"""
import sys
import time


class ActivityMonitor:
    """活动监控器 - 检测用户空闲时间"""
    
    def __init__(self):
        self._last_input_time = None
        self._platform = sys.platform
        
        # Windows 平台初始化
        if self._platform.startswith("win"):
            self._init_windows()
        else:
            # 非 Windows 平台使用降级实现
            self._init_fallback()
    
    def _init_windows(self):
        """初始化 Windows API"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # 定义 LASTINPUTINFO 结构体
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_uint),
                    ("dwTime", ctypes.c_uint),
                ]
            
            self._user32 = ctypes.windll.user32
            self._kernel32 = ctypes.windll.kernel32
            
            # 获取函数指针
            self._GetLastInputInfo = self._user32.GetLastInputInfo
            self._GetLastInputInfo.argtypes = [ctypes.POINTER(LASTINPUTINFO)]
            self._GetLastInputInfo.restype = wintypes.BOOL
            
            # 优先使用 GetTickCount64（64位，避免溢出）
            try:
                self._GetTickCount64 = self._kernel32.GetTickCount64
                self._GetTickCount64.restype = ctypes.c_ulonglong
                self._use_64bit = True
            except AttributeError:
                # 降级到 32 位（可能溢出，但不常见）
                self._GetTickCount = self._kernel32.GetTickCount
                self._GetTickCount.restype = wintypes.DWORD
                self._use_64bit = False
            
            self._LASTINPUTINFO = LASTINPUTINFO
            self._ctypes = ctypes
            self._windows_available = True
            
        except Exception as e:
            print(f"警告: Windows API 初始化失败: {e}")
            print("将使用降级实现（总是返回空闲）")
            self._windows_available = False
            self._init_fallback()
    
    def _init_fallback(self):
        """降级实现（非 Windows 或 Windows API 失败）"""
        self._windows_available = False
        if not self._platform.startswith("win"):
            print(f"提示: 平台 {self._platform} 未实现空闲检测")
            print("将使用降级实现（总是允许显示）")
    
    def get_idle_seconds(self) -> float:
        """
        获取空闲时间（秒）
        
        :return: 空闲秒数，如果检测失败返回一个很大的值（总是允许显示）
        """
        if self._platform.startswith("win") and self._windows_available:
            return self._get_idle_seconds_windows()
        else:
            # 降级实现：返回一个很大的值，表示"总是空闲"（总是允许显示）
            return 999999.0
    
    def _get_idle_seconds_windows(self) -> float:
        """Windows 平台获取空闲时间"""
        try:
            # 创建 LASTINPUTINFO 结构体
            last_input_info = self._LASTINPUTINFO()
            last_input_info.cbSize = self._ctypes.sizeof(self._LASTINPUTINFO)
            
            # 获取最后输入时间
            if not self._GetLastInputInfo(self._ctypes.byref(last_input_info)):
                # API 调用失败，返回默认值
                return 999999.0
            
            # 获取当前系统运行时间
            if self._use_64bit:
                current_tick = self._GetTickCount64()
                last_input_tick = last_input_info.dwTime
            else:
                current_tick = self._GetTickCount()
                last_input_tick = last_input_info.dwTime
                # 处理 32 位溢出（虽然不常见，但需要处理）
                if current_tick < last_input_tick:
                    # 发生了溢出，需要调整
                    current_tick += 0xFFFFFFFF
            
            # 计算空闲时间（毫秒）
            idle_ms = current_tick - last_input_tick
            
            # 转换为秒
            idle_seconds = idle_ms / 1000.0
            
            return idle_seconds
            
        except Exception as e:
            print(f"警告: 获取空闲时间失败: {e}")
            # 失败时返回默认值（总是允许显示）
            return 999999.0
