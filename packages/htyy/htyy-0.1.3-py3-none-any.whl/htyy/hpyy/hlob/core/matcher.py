# core/matcher.py
import re

def glob_to_regex(pattern: str) -> str:
    # 转义正则中的特殊字符（如 . ^ $）
    pattern = re.escape(pattern)
    
    # 将 glob 通配符替换为正则表达式
    pattern = pattern.replace(r'\*', '.*')    # * → 任意字符
    pattern = pattern.replace(r'\?', '.')     # ? → 单个字符
    pattern = pattern.replace(r'\[', '[')     # 恢复 [] 的原始含义
    pattern = pattern.replace(r'\]', ']')
    pattern = pattern.replace(r'\!', '^')     # [!a] → [^a]
    
    # 添加边界匹配（确保精确匹配文件名）
    return f'^{pattern}$'