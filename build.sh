#!/bin/bash
# Float Words - 打包脚本 (Linux/Mac)

echo "========================================"
echo "Float Words - 打包脚本"
echo "========================================"
echo ""

# 检查是否安装了PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[错误] 未安装 PyInstaller"
    echo "正在安装 PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[错误] PyInstaller 安装失败"
        exit 1
    fi
fi

echo "[信息] 开始打包..."
echo ""

# 清理之前的构建文件
rm -rf build dist FloatWords.spec

# 使用spec文件打包
pyinstaller build_exe.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 打包失败！"
    exit 1
fi

echo ""
echo "========================================"
echo "打包完成！"
echo "========================================"
echo ""
echo "可执行文件位置: dist/FloatWords"
echo ""
echo "提示："
echo "- 首次运行可能需要几秒钟启动"
echo "- 在Linux上可能需要添加执行权限: chmod +x dist/FloatWords"
echo ""
