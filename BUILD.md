# 打包指南

本指南说明如何将 Float Words 打包为可执行文件。

## 前置要求

1. 确保已安装 Python 3.7 或更高版本
2. 确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

## Windows 打包

### 方法一：使用打包脚本（推荐）

1. 安装 PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 运行打包脚本：
   ```bash
   build.bat
   ```

3. 打包完成后，可执行文件位于 `dist\FloatWords.exe`

### 方法二：手动打包

1. 安装 PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 运行 PyInstaller：
   ```bash
   pyinstaller build_exe.spec
   ```

3. 打包完成后，可执行文件位于 `dist\FloatWords.exe`

## Linux/Mac 打包

### 方法一：使用打包脚本（推荐）

1. 安装 PyInstaller：
   ```bash
   pip3 install pyinstaller
   ```

2. 添加执行权限并运行脚本：
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

3. 打包完成后，可执行文件位于 `dist/FloatWords`

### 方法二：手动打包

1. 安装 PyInstaller：
   ```bash
   pip3 install pyinstaller
   ```

2. 运行 PyInstaller：
   ```bash
   pyinstaller build_exe.spec
   ```

3. 打包完成后，可执行文件位于 `dist/FloatWords`

## 打包选项说明

### build_exe.spec 文件说明

- `name='FloatWords'`: 可执行文件名称
- `console=False`: 不显示控制台窗口（GUI应用）
- `icon=None`: 图标文件路径（需要.ico格式，可选）
- `datas`: 包含的数据文件列表
  - `('data/texts.txt', 'data')`: 将文本文件包含到打包文件中

### 自定义图标

如果需要自定义图标：

1. 准备一个 `.ico` 格式的图标文件（Windows）或 `.icns` 格式（Mac）
2. 将图标文件放在项目根目录
3. 编辑 `build_exe.spec` 文件，修改 `icon` 参数：
   ```python
   icon='icon.ico',  # Windows
   # 或
   icon='icon.icns',  # Mac
   ```

## 常见问题

### 1. 打包后程序无法启动

- 检查是否有杀毒软件拦截
- 尝试在命令行运行，查看错误信息
- 检查是否缺少必要的依赖

### 2. 打包后找不到文本文件

- 确保 `data/texts.txt` 文件存在
- 检查 `build_exe.spec` 中的 `datas` 配置是否正确

### 3. 打包文件过大

- 这是正常的，因为包含了 Python 解释器和所有依赖
- 可以使用 UPX 压缩（已在配置中启用）
- 或者使用 `--onefile` 模式（已在配置中使用）

### 4. 首次运行较慢

- 这是正常的，因为需要解压临时文件
- 后续运行会更快

## 测试打包后的程序

1. 运行打包后的可执行文件
2. 检查功能是否正常：
   - 启动对话框是否显示
   - 文字是否正常显示
   - 系统托盘菜单是否正常
   - 热键是否正常工作

## 分发

打包完成后，可以：

1. 直接分发 `dist/FloatWords.exe`（Windows）或 `dist/FloatWords`（Linux/Mac）
2. 用户无需安装 Python 即可运行
3. 建议在多个系统上测试后再分发
