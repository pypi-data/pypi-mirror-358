# utils.py
import os
import platform

def normalize_path(path: str) -> str:
    # 统一路径分隔符为 /
    path = path.replace(os.sep, '/')
    
    # 处理 Windows 大小写不敏感
    if platform.system() == 'Windows':
        path = path.lower()
    return path