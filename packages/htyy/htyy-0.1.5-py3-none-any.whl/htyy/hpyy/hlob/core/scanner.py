# core/scanner.py
import os
from typing import List

def scan_directory(root: str, recursive: bool = False) -> List[str]:
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        # 处理非递归模式（仅当前目录）
        if not recursive:
            dirnames.clear()  # 阻止进入子目录
        for filename in filenames + dirnames:
            full_path = os.path.join(dirpath, filename)
            matches.append(full_path)
    return matches