"""
配置文件
包含所有可配置的常量
"""
import os as _os
# 装饰图标
DECOR_ICONS = ["💓", "💕", "🌸", "💝", "✨", "🌷"]

# 颜色主题 (背景色, 文字色)
COLOR_THEMES = [
    ("#4A4A4A", "rgba(255, 255, 255, 200)"),
    ("#5C6F7B", "rgba(232, 240, 245, 210)"),
    ("#6B5B95", "rgba(240, 232, 248, 210)"),
    ("#7A5C3E", "rgba(248, 240, 230, 210)"),
    ("#3E6F5C", "rgba(232, 248, 240, 210)"),
    ("#7A4F55", "rgba(248, 232, 236, 210)"),
]

# 夜间模式主题
NIGHT_THEMES = [
    ("#FFFFFF", "rgba(50,50,50,200)"),
    ("#FFD700", "rgba(60,60,60,200)")
]

# 应用设置
MAX_FLOATS = 6
FONT_NAME = "SimHei"
FONT_SIZE = 18
LIFETIME = 7000  # 文字显示时长（毫秒）
SPAWN_INTERVAL = 1800  # 生成间隔（毫秒）
FLOAT_SPEED = 40  # 漂浮速度（毫秒）

# 空闲检测设置
IDLE_ONLY = True  # 是否仅在空闲时显示
IDLE_THRESHOLD_SECONDS = 30  # 空闲阈值（秒）
DEBUG = True  # 调试模式（显示详细日志）

# 文本来源与 AI 配置
TEXT_SOURCE = "auto"  # auto / local / ai
AI_ENABLED = True
AI_PROVIDER = "deepseek"
AI_API_BASE = "https://api.deepseek.com"  # 不带 /v1，后续拼接
# ⚠️ 不要把 API Key 写进仓库！请使用环境变量：DEEPSEEK_API_KEY

AI_API_KEY = _os.getenv("DEEPSEEK_API_KEY", "")
AI_MODEL = "deepseek-chat"
AI_TEMPERATURE = 0.8
AI_ITEMS_PER_DAY = 50  # 每天生成多少条
AI_CACHE_DIR = "data/ai_cache"
AI_TIMEOUT_SECONDS = 60
AI_FAILOVER_TO_LOCAL = True  # AI 失败时是否回退到本地文本

# Prompt 模板（必须只输出 JSON）
AI_PROMPT_TEMPLATE = """
你是一个桌面漂浮文字生成器。请为今天生成 {n} 条简短、温和、不打扰的中文漂浮文字。
输出必须是严格 JSON，不要包含任何解释、Markdown 或多余字符。

约束：
- 每条 text 5~22 个汉字左右，尽量不超过 26 字
- 避免命令式、避免说教、避免夸张鸡汤
- 不包含敏感/政治/暴力/色情内容
- 不要出现网址、@、#、表情符号
- 不要重复句子
- 如果提供了称呼（salutation），可以在少部分句子里轻柔地使用这个称呼，但不要过度重复。

用户自定义偏好（可能为空）：
- {user_custom_prompt}

上下文（可能为空）：
- 日期：{date}
- 星期：{weekday}
- 时间段：{time_of_day}
- 城市：{city}
- 天气：{weather}
- 称呼：{salutation}

请返回 JSON，结构如下：
{{
  "date": "{date}",
  "items": [
    {{"text": "…", "tags": ["gentle"], "weight": 1}}
  ]
}}
""".strip()

# 文本文件路径
TEXT_FILE = "data/texts.txt"

# 热键设置
HOTKEY_EXIT = "alt+s"
