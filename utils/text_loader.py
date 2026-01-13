"""
文本加载器
从文件或默认列表加载文本
"""
import os
import sys
from config import TEXT_FILE


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径
    支持开发环境和PyInstaller打包后的环境
    """
    try:
        # PyInstaller创建的临时文件夹路径
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境，使用当前文件所在目录
        base_path = os.path.abspath(os.path.dirname(__file__))
        # 回到项目根目录
        base_path = os.path.dirname(os.path.dirname(base_path))
    
    return os.path.join(base_path, relative_path)


def load_texts():
    """
    加载文本列表
    优先从文件加载，如果文件不存在则返回默认列表
    """
    default_texts = [
        "Her gün enerji dolu yaşa",
        "Zamanında yemek yiyin, midenizi koruyun",
        "Kendinde potansiyel olduğunu inanın",
        "Yorgun olduğunda dinlenin, zorlanmayın",
        "Meraklı kalın, dünyayı keşfedin",
        "Her deneme, bir gelişimdir",
        "Şu anı yaşayın, zamanı boşa harcamayın",
        "Gülümserek insanlarla karşılaşın, dünyayı ısıtın",
        "Sabırlı olun, sürprizler bekliyor, vazgeçmeyin",
        "Doğaya yakınlaşın, ruh huzur bulsun",
    ]
    
    # 获取资源文件路径
    text_file_path = get_resource_path(TEXT_FILE)
    
    if os.path.exists(text_file_path):
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                texts = []
                for line in f:
                    line = line.strip()
                    # 移除引号和逗号（如果存在）
                    if line.startswith('"') and line.endswith('",'):
                        line = line[1:-2]
                    elif line.startswith('"') and line.endswith('"'):
                        line = line[1:-1]
                    if line:
                        texts.append(line)
                if texts:
                    return texts
        except Exception as e:
            print(f"读取文本文件失败: {e}")
    
    return default_texts
