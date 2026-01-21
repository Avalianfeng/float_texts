"""
应用控制器
负责窗口生命周期管理、生成控制、退出清理
"""
import random
import threading
import time
from enum import Enum
from typing import Set
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QApplication
from core.spawner import FloatSpawner
from core.activity_monitor import ActivityMonitor
from core.text_provider import BaseTextProvider, LocalTextProvider
from core.text_provider.deepseek_provider import DeepSeekTextProvider
from ui.float_text import FloatText
from utils.text_loader import load_texts
from config import (
    DEBUG,
    AI_FAILOVER_TO_LOCAL,
)
from core import settings as app_settings


class AppState(Enum):
    """应用状态"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    EXITING = "exiting"


class AppController(QObject):
    """应用控制器 - 统一管理窗口生命周期和生成逻辑"""
    
    # 状态改变信号
    stateChanged = pyqtSignal(bool)  # running: bool
    providerChanged = pyqtSignal(str)  # "local" / "ai"
    aiPreparingChanged = pyqtSignal(bool)
    
    def __init__(self, spawner: FloatSpawner = None, activity_monitor: ActivityMonitor = None):
        super().__init__()
        
        # 创建或使用传入的 spawner
        self.spawner = spawner if spawner else FloatSpawner()
        
        # 创建或使用传入的 activity monitor
        self.activity_monitor = activity_monitor if activity_monitor else ActivityMonitor()
        
        # 设置（运行时优先使用 settings，config 作为默认兜底）
        self.idle_only = app_settings.get_idle_only()
        self.idle_threshold_seconds = app_settings.get_idle_threshold_seconds()
        self.max_floats = app_settings.get_max_floats()
        
        # 文本 Provider 管理
        self.local_provider: BaseTextProvider = LocalTextProvider()
        self.ai_provider: DeepSeekTextProvider | None = None
        self.text_provider: BaseTextProvider = self.local_provider
        self.ai_enabled: bool = app_settings.get_ai_enabled()
        self.text_source: str = app_settings.get_text_source()
        self._ai_preparing: bool = False
        self._ai_last_attempt_ts: float | None = None
        self._ai_backoff_seconds: int = 60  # 自动重试退避（可后续配置化）
        
        # 先准备本地 provider，保证立即可用
        self.local_provider.prepare()
        if DEBUG:
            print(f"[Provider] Local provider ready={self.local_provider.is_ready()}")
        
        # 窗口管理（使用普通 set，因为已经通过信号自动移除）
        # 注意：WeakSet 不支持 len()，所以使用普通 set
        self.float_windows: Set[QWidget] = set()
        
        # 状态管理
        self._state = AppState.STOPPED
        
        # 连接 spawner 的信号
        self.spawner.spawnRequested.connect(self._on_spawn_requested)
        
        # 根据配置异步准备 AI Provider
        if self.ai_enabled and self.text_source in ("auto", "ai"):
            self._prepare_ai_provider_async()

    def _prepare_ai_provider_async(self) -> None:
        # single-flight + backoff，避免并发重试把网络拖死
        now = time.time()
        if self._ai_preparing:
            if DEBUG:
                print("[Provider] AI 正在准备中，跳过重复触发")
            return
        if self._ai_last_attempt_ts and (now - self._ai_last_attempt_ts) < self._ai_backoff_seconds:
            if DEBUG:
                wait = self._ai_backoff_seconds - (now - self._ai_last_attempt_ts)
                print(f"[Provider] AI 退避中，{wait:.0f}s 后再试（如需可点“刷新今日 AI 文本”）")
            return

        self._ai_preparing = True
        self._ai_last_attempt_ts = now
        self.aiPreparingChanged.emit(True)
        threading.Thread(target=self._prepare_ai_provider, daemon=True).start()

    # ---------- Provider 管理 ----------

    def _prepare_ai_provider(self) -> None:
        """在后台线程中准备 AI Provider"""
        try:
            provider = DeepSeekTextProvider()
            provider.prepare()
            if not provider.is_ready():
                if DEBUG:
                    print("[Provider] AI provider 未就绪，保持使用本地文本")
                return
            self.ai_provider = provider
            if DEBUG:
                print("[Provider] AI provider 已就绪")

            # 根据 text_source 决定是否切换
            if self.ai_enabled and self.text_source in ("auto", "ai"):
                # 切换到 AI provider
                self.text_provider = self.ai_provider
                self.providerChanged.emit("ai")
                if DEBUG:
                    print(f"[Provider] 已切换到 AI provider (mode={self.text_source})")
        except Exception as e:
            if DEBUG:
                print(f"[Provider] 准备 AI provider 失败: {e}")
        finally:
            self._ai_preparing = False
            self.aiPreparingChanged.emit(False)

    def set_ai_enabled(self, enabled: bool) -> None:
        """启用/禁用 AI 文本（禁用时切回本地）"""
        self.ai_enabled = enabled
        if not enabled:
            self.text_provider = self.local_provider
            self.providerChanged.emit("local")
            if DEBUG:
                print("[Provider] 已切回本地 provider（AI disabled）")
            return

        # enabled=True：如果 AI 已就绪则切换，否则后台准备
        if self.ai_provider and self.ai_provider.is_ready():
            self.text_provider = self.ai_provider
            self.providerChanged.emit("ai")
            if DEBUG:
                print("[Provider] 已切换到 AI provider（AI enabled）")
        else:
            if DEBUG:
                print("[Provider] AI provider 未就绪，后台准备中…")
            self._prepare_ai_provider_async()

    def set_text_source(self, source: str) -> None:
        """设置文本来源（auto/local/ai）并立即应用"""
        src = (source or "").lower()
        if src not in ("auto", "local", "ai"):
            return
        self.text_source = src

        if src == "local":
            self.text_provider = self.local_provider
            self.providerChanged.emit("local")
            return

        # auto/ai：若 AI 可用则切换，否则准备
        if self.ai_enabled and self.ai_provider and self.ai_provider.is_ready():
            self.text_provider = self.ai_provider
            self.providerChanged.emit("ai")
        elif self.ai_enabled:
            self._prepare_ai_provider_async()

    def apply_settings(self, changed_keys: list) -> None:
        """
        SettingsDialog 保存后调用：按 changed_keys 进行最小化热更新。
        规则：
        - idle_only/threshold：立即生效
        - ai_enabled/text_source：立即切换/准备
        - city（以及未来 weather）：不自动重生成，提示用户手动刷新今日 AI 文本
        """
        keys = set(changed_keys or [])

        if app_settings.Keys.IDLE_ENABLED in keys:
            self.idle_only = app_settings.get_idle_only()
            if DEBUG:
                print(f"[Settings] idle_only={self.idle_only}")

        if app_settings.Keys.IDLE_THRESHOLD_SECONDS in keys:
            self.idle_threshold_seconds = app_settings.get_idle_threshold_seconds()
            if DEBUG:
                print(f"[Settings] idle_threshold_seconds={self.idle_threshold_seconds}")

        if app_settings.Keys.UI_FLOAT_DENSITY in keys:
            self.max_floats = app_settings.get_max_floats()
            if DEBUG:
                print(f"[Settings] max_floats={self.max_floats}")

        if app_settings.Keys.UI_FLOAT_SPEED in keys:
            # 速度由 FloatText 在创建时读取 settings；这里给提示即可
            if DEBUG:
                print(f"[Settings] float_speed={app_settings.get_float_speed_label()} ({app_settings.get_float_speed_ms()}ms)")

        if app_settings.Keys.AI_ENABLED in keys:
            self.set_ai_enabled(app_settings.get_ai_enabled())
            if DEBUG:
                print(f"[Settings] ai_enabled={self.ai_enabled}")

        if app_settings.Keys.AI_TEXT_SOURCE in keys:
            self.set_text_source(app_settings.get_text_source())
            if DEBUG:
                print(f"[Settings] text_source={self.text_source}")

        if app_settings.Keys.AI_DEEPSEEK_API_KEY in keys:
            # 如果用户刚配置了 key，且当前需要 AI，则尝试准备
            if self.ai_enabled and self.text_source in ("auto", "ai"):
                self._prepare_ai_provider_async()

        if app_settings.Keys.CONTEXT_CITY in keys:
            # 不自动刷新缓存，避免频繁打 API
            print("[Settings] 城市已更新：需要“刷新今日 AI 文本”后才会影响今日文本。")

    def refresh_today_ai(self) -> None:
        """强制刷新今日 AI 文本（删除缓存并重新生成，异步）"""
        if not self.ai_enabled:
            if DEBUG:
                print("[Provider] AI 未启用，忽略刷新")
            return

        if self._ai_preparing:
            if DEBUG:
                print("[Provider] AI 正在准备中，暂不允许刷新")
            return

        self._ai_preparing = True
        self.aiPreparingChanged.emit(True)

        def worker():
            try:
                if self.ai_provider is None:
                    self.ai_provider = DeepSeekTextProvider()
                else:
                    self.ai_provider.invalidate_today_cache()
                self.ai_provider.prepare()
                if self.ai_provider.is_ready():
                    self.text_provider = self.ai_provider
                    self.providerChanged.emit("ai")
                    if DEBUG:
                        print("[Provider] 今日 AI 文本已刷新并启用")
                else:
                    if DEBUG:
                        print("[Provider] 刷新失败，保持当前 provider")
            except Exception as e:
                if DEBUG:
                    print(f"[Provider] 刷新 AI 文本失败: {e}")
            finally:
                self._ai_preparing = False
                self.aiPreparingChanged.emit(False)

        threading.Thread(target=worker, daemon=True).start()
    
    @property
    def state(self) -> AppState:
        """获取当前状态"""
        return self._state
    
    @property
    def running(self) -> bool:
        """是否正在运行"""
        return self._state == AppState.RUNNING
    
    def start(self):
        """启动生成"""
        if self._state == AppState.EXITING:
            return
        
        self._state = AppState.RUNNING
        self.spawner.start()
        self.stateChanged.emit(True)
    
    def pause(self):
        """暂停生成（不关闭现有窗口）"""
        if self._state == AppState.EXITING:
            return
        
        self._state = AppState.PAUSED
        self.spawner.stop()
        self.stateChanged.emit(False)
    
    def stop(self):
        """停止生成并关闭所有窗口"""
        self._state = AppState.STOPPED
        self.spawner.stop()
        self._close_all_windows()
        self.stateChanged.emit(False)
    
    def exit(self):
        """退出应用"""
        # 防止重复退出
        if self._state == AppState.EXITING:
            return
        
        self._state = AppState.EXITING
        
        # 停止生成
        self.spawner.stop()
        
        # 关闭所有窗口
        self._close_all_windows()
        
        # 发出状态改变信号
        self.stateChanged.emit(False)
        
        # 退出应用
        app = QApplication.instance()
        if app:
            app.quit()
    
    def _on_spawn_requested(self):
        """处理生成请求"""
        # 如果处于暂停或退出状态，不生成
        if self._state != AppState.RUNNING:
            return
        
        # 空闲检测门控
        if self.idle_only:
            try:
                idle_seconds = self.activity_monitor.get_idle_seconds()
                threshold = self.idle_threshold_seconds
                if idle_seconds < threshold:
                    if DEBUG:
                        print(f"[DEBUG] idle={idle_seconds:.1f}s < {threshold}s, skip spawn")
                    return
                elif DEBUG:
                    print(f"[DEBUG] idle={idle_seconds:.1f}s >= {threshold}s, allow spawn")
            except Exception as e:
                # 空闲检测失败时，默认允许生成（避免完全不生成）
                if DEBUG:
                    print(f"[DEBUG] idle检测失败: {e}, 默认允许生成")
        
        # 检查窗口数量限制
        self._cleanup_invisible_windows()
        if len(self.float_windows) >= self.max_floats:
            if DEBUG:
                print(f"[DEBUG] 窗口数量已达上限 {self.max_floats}, skip spawn")
            return
        
        # 获取下一个文本并生成窗口
        text = self._get_next_text()
        self._spawn_one(text)
    
    def _get_next_text(self) -> str:
        """从当前 Provider 获取一条文本，必要时回退到本地"""
        # 优先使用当前 provider
        provider = self.text_provider or self.local_provider
        text = ""
        try:
            if provider and provider.is_ready():
                text = provider.get_next_text()
        except Exception as e:
            if DEBUG:
                print(f"[Provider] 获取文本失败: {e}")
            text = ""

        # 如果文本为空且允许回退，则使用本地 provider
        if (not text) and AI_FAILOVER_TO_LOCAL:
            if provider is not self.local_provider and self.local_provider.is_ready():
                try:
                    text = self.local_provider.get_next_text()
                    if DEBUG:
                        print("[Provider] 已回退到本地文本")
                except Exception as e:
                    if DEBUG:
                        print(f"[Provider] 本地文本获取失败: {e}")

        # 最后兜底：简单固定文本
        if not text:
            text = "保持放松，慢慢来。"

        return text
    
    def _spawn_one(self, text: str):
        """生成一个漂浮文字窗口"""
        try:
            window = FloatText(text)
            # 设置关闭时自动删除
            window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            
            # 连接窗口关闭信号（使用闭包捕获 window）
            def on_closed(w=window):
                self._remove_window(w)
            
            window.closed.connect(on_closed)
            
            # 连接 destroyed 信号作为备用（使用弱引用避免循环引用）
            def on_destroyed(obj=None):
                # destroyed 信号会传递对象，但此时对象可能已经部分销毁
                # 使用 try-except 安全移除
                try:
                    if window in self.float_windows:
                        self._remove_window(window)
                except:
                    pass
            
            window.destroyed.connect(on_destroyed)
            
            # 添加到窗口集合
            self.float_windows.add(window)
        except Exception as e:
            print(f"生成窗口失败: {e}")
    
    def _on_window_closed(self, window: QWidget):
        """窗口关闭回调"""
        self._remove_window(window)
    
    def _remove_window(self, window: QWidget):
        """从集合中移除窗口"""
        if window in self.float_windows:
            self.float_windows.discard(window)
    
    def _cleanup_invisible_windows(self):
        """清理不可见的窗口"""
        to_remove = [w for w in self.float_windows if not w.isVisible()]
        for window in to_remove:
            self._remove_window(window)
    
    def _close_all_windows(self):
        """关闭所有窗口"""
        # 创建副本避免迭代时修改集合
        windows_to_close = list(self.float_windows)
        
        for window in windows_to_close:
            try:
                if window and window.isVisible():
                    # 使用强制关闭，立即关闭窗口
                    if hasattr(window, 'force_close'):
                        window.force_close()
                    else:
                        window.close()
            except Exception:
                pass
        
        # 清空集合（即使关闭失败也要清空，避免内存泄漏）
        self.float_windows.clear()
