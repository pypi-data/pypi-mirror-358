# core/__init__.py
import os
import re
from .matcher import glob_to_regex
from .scanner import scan_directory
from ..utils import normalize_path
from typing import List

def hlob(pattern: str) -> List[str]:
    # 分离目录和文件名部分（例如：src/**/*.py → 目录=src, 文件名=*.py）
    dir_part, name_part = os.path.split(pattern)
    
    # 处理递归通配符 `**`
    recursive = '**' in dir_part
    if recursive:
        dir_part = dir_part.replace('**', '')  # 简化逻辑
    
    # 扫描目录
    files = scan_directory(dir_part or '.', recursive=recursive)
    
    # 转换文件名通配符为正则表达式
    regex = re.compile(glob_to_regex(name_part))
    
    # 过滤匹配项
    matched = []
    for file in files:
        # 标准化路径并提取文件名
        normalized = normalize_path(file)
        dir_name, file_name = os.path.split(normalized)
        
        # 匹配文件名部分
        if regex.match(file_name):
            matched.append(file)
    
    return matched