"""
资源文件路径工具

统一处理资源文件路径，支持开发环境和 PyInstaller 打包环境
"""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径
    
    支持开发环境和 PyInstaller 打包后的环境
    
    Args:
        relative_path: 相对于项目根目录的路径，如 "icon.png" 或 "data/texts.txt"
    
    Returns:
        资源文件的绝对路径
    """
    try:
        # PyInstaller 创建的临时文件夹路径
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境，使用当前文件所在目录
        base_path = os.path.abspath(os.path.dirname(__file__))
        # 回到项目根目录（utils -> 项目根）
        base_path = os.path.dirname(base_path)
    
    return os.path.join(base_path, relative_path)


def get_icon_path() -> tuple[str, str]:
    """
    获取图标文件路径（优先 .ico，其次 .png）
    
    Returns:
        (icon_path, fallback_path) 元组
        icon_path: 优先使用的图标路径（.ico）
        fallback_path: 备用图标路径（.png）
    """
    icon_ico = get_resource_path("icon.ico")
    icon_png = get_resource_path("icon.png")
    
    # 如果 .ico 存在，优先使用
    if os.path.exists(icon_ico):
        return (icon_ico, icon_png)
    else:
        return (icon_png, icon_png)
