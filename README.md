# Float Words - 漂浮文字桌面伴侣

一个优雅的桌面提醒工具，会在你空闲时显示温馨的文字提醒。

## 功能特性

- 🌸 优雅的漂浮文字动画
- 🌙 自动夜间模式切换
- 💤 智能空闲检测
- 🎨 多种颜色主题
- 🔔 系统托盘支持
- ⌨️ 全局热键控制

## 项目结构

```
float_words/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
├── README.md           # 项目说明
├── data/               # 数据目录
│   └── texts.txt       # 文本内容文件
├── ui/                 # UI组件
│   ├── float_text.py   # 漂浮文字窗口
│   ├── start_dialog.py # 启动对话框
│   └── tray.py         # 系统托盘
├── core/               # 核心逻辑
│   ├── spawner.py      # 文字生成器
│   ├── idle_detector.py # 空闲检测
│   └── hotkey.py       # 热键管理
└── utils/              # 工具模块
    ├── theme.py        # 主题管理
    └── text_loader.py  # 文本加载器
```

## 安装

1. 克隆或下载项目
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

运行主程序：
```bash
python main.py
```

### 控制方式

- **系统托盘菜单**：右键点击系统托盘图标
  - 暂停/继续：暂停或恢复文字显示
  - 退出：退出程序
- **全局热键**：按 `Alt + S` 退出程序

## 配置说明

所有配置都在 `config.py` 文件中，可以修改：

- `MAX_FLOATS`: 同时显示的最大文字数量
- `FONT_NAME`: 字体名称
- `FONT_SIZE`: 字体大小
- `LIFETIME`: 文字显示时长（毫秒）
- `SPAWN_INTERVAL`: 生成间隔（毫秒）
- `FLOAT_SPEED`: 漂浮速度（毫秒）
- `IDLE_THRESHOLD`: 空闲检测阈值（秒）

## 文本内容

文本内容存储在 `data/texts.txt` 文件中，每行一条。程序会自动加载该文件，如果文件不存在则使用默认文本。

## 工作原理

1. **空闲检测**：程序会检测鼠标和键盘活动，当用户空闲超过设定时间后，开始显示文字
2. **智能暂停**：当用户重新活动时，自动暂停显示
3. **主题切换**：根据时间自动切换日间/夜间主题（19:00-7:00为夜间模式）

## 依赖说明

- **PyQt6**: GUI框架
- **keyboard**: 全局热键支持
- **mouse**: 鼠标活动检测

## 许可证

本项目仅供学习和个人使用。
# float_texts
