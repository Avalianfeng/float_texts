# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件
用于生成可执行文件
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/texts.txt', 'data'),  # 包含文本数据文件
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'ui.float_text',
        'ui.start_dialog',
        'core.spawner',
        'utils.theme',
        'utils.text_loader',
        'config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FloatWords',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有图标文件，可以在这里指定路径，如: 'icon.ico'
    # 注意：Windows需要.ico格式，Mac需要.icns格式
    # 可以使用在线工具将.png转换为.ico: https://convertio.co/zh/png-ico/
)
