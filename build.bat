@echo off
chcp 65001 >nul
echo ========================================
echo Float Words - 打包脚本
echo ========================================
echo.

REM 检查是否安装了PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [错误] 未安装 PyInstaller
    echo 正在安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败
        pause
        exit /b 1
    )
)

echo [信息] 开始打包...
echo.

REM 清理之前的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist FloatWords.spec del /q FloatWords.spec

REM 使用spec文件打包
pyinstaller build_exe.spec

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\FloatWords.exe
echo.
echo 提示：
echo - 首次运行可能需要几秒钟启动
echo - 如果被杀毒软件拦截，请添加信任
echo.
pause
