# Float Words（漂浮文字桌面伴侣）

一个基于 **PyQt6** 的桌面小工具：在屏幕上弹出轻量、半透明的漂浮文字（本地文本或 AI 生成），并通过 **系统托盘**进行控制。

## 功能概览

- **托盘控制**：开始 / 暂停 / 仅空闲时显示 / 刷新今日 AI 文本 / 设置… / 退出
- **空闲检测（Windows）**：默认仅在空闲超过阈值时生成，避免打扰
- **AI 文本（DeepSeek，可选）**：每日生成并缓存到 `data/ai_cache/`，失败自动回退本地文本
- **设置窗口（QSettings）**：无需改 `config.py`，API Key 不进仓库（本机保存）
- **资源**：支持 `icon.png` / `icon.ico`

## 快速开始

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 运行

```bash
python main.py
```

运行后会出现托盘图标；从托盘点击 **开始** 即可显示漂浮文字。

## 配置方式（推荐）

从托盘菜单打开 **设置…**（`ui/settings_dialog.py`）进行配置，配置项会写入 **QSettings**：

- **AI**：启用 AI（DeepSeek）
- **文本来源**：`auto / local / ai`
- **DeepSeek API Key**：本机保存（密码输入框）
- **城市 City**：可空（用于 AI prompt 的可选上下文）
- **仅空闲时显示 / 空闲阈值**

### DeepSeek Key 的读取优先级（重要）

程序读取 Key 的优先级为：

1. 环境变量 `DEEPSEEK_API_KEY`
2. 设置窗口保存的 Key（QSettings）
3. `config.py` 的 `AI_API_KEY`（兜底，通常为空）

## 文本来源与缓存

- **本地文本**：`data/texts.txt`（每行一条）
- **AI 文本缓存**：`data/ai_cache/YYYY-MM-DD.json`
  - 当天多次启动会复用缓存，不会重复请求
  - 修改 City/上下文后：需要从托盘点击 **刷新今日 AI 文本** 才会让“今天的文本包”使用新上下文

## 项目结构（当前）

```
float_words/
├── main.py
├── config.py
├── requirements.txt
├── icon.png / icon.ico
├── data/
│   ├── texts.txt
│   └── ai_cache/
├── core/
│   ├── app_controller.py        # 生命周期/生成门控/provider 切换
│   ├── spawner.py               # QTimer 调度生成请求
│   ├── activity_monitor.py      # Windows 空闲检测
│   ├── settings.py              # QSettings 封装（持久化配置）
│   ├── context/                 # Phase D：可选上下文（city/weather）
│   └── text_provider/           # Phase C：文本提供者（local / deepseek）
├── ui/
│   ├── tray.py                  # 托盘菜单
│   ├── settings_dialog.py       # 设置窗口
│   ├── start_dialog.py
│   └── float_text.py
└── tools/
    └── test_deepseek.py         # DeepSeek 连通性/代理测试
```

## 常见问题

### 1) 为什么会走代理？

`requests` 会自动读取系统/环境代理（如 `HTTP_PROXY/HTTPS_PROXY`）。你可以用 `tools/test_deepseek.py` 查看当前是否走代理：

```bash
python tools/test_deepseek.py
```

### 2) AI 超时/不稳定怎么办？

- 优先检查代理是否稳定
- 适当增大 `config.py` 的 `AI_TIMEOUT_SECONDS`
- 先把 `AI_ITEMS_PER_DAY` 调小验证链路，再逐步调回

## 打包说明（当前仓库未提供脚本/Spec）

本仓库当前 **没有**内置 `PyInstaller .spec` 或 `build.bat/build.sh` 脚本；如需打包我可以再补一套“最小可用的 PyInstaller 配置”（包含数据文件与图标）。

## 许可证

本项目仅供学习和个人使用。
