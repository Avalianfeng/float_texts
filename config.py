"""
配置文件
包含所有可配置的常量
"""

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
IDLE_THRESHOLD = 60  # 空闲阈值（秒）

# 文本文件路径
TEXT_FILE = "data/texts.txt"

# 图标文件路径
ICON_FILE = "icon.png"

# 热键设置
HOTKEY_EXIT = "alt+s"
