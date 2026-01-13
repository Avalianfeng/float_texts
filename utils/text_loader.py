"""
文本加载器
从文件或默认列表加载文本
"""
import os
from config import TEXT_FILE


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
    
    if os.path.exists(TEXT_FILE):
        try:
            with open(TEXT_FILE, 'r', encoding='utf-8') as f:
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
