"""
文本加载器
从文件或默认列表加载文本
"""
import os
from config import TEXT_FILE
from utils.resources import get_resource_path


def load_texts():
    """
    加载文本列表
    优先从文件加载，如果文件不存在则返回默认列表
    """
    default_texts =[
    "过充满活力的每一天",
    "按时吃饭，保护胃。",
    "相信自己有潜力",
    "累了就休息别勉强",
    "保持好奇心探索世界",
    "每一次试验都是一次发展",
    "活在当下不要浪费时间",
    "遇见微笑的人温暖世界",
    "耐心等待惊喜不要放弃",
    "亲近自然愿灵魂得到安宁"
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
