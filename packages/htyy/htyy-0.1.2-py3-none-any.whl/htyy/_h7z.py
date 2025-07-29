"""
7z 高级工具 - 独立函数版
功能：压缩/解压、加密算法选择、分卷、多线程、哈希校验等
依赖：py7zr, tqdm, cryptography
安装：pip install py7zr tqdm cryptography
"""
import os
import sys
import argparse
import hashlib
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Callable
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import py7zr
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher
from cryptography.hazmat.backends import default_backend
import webdriver_manager

# ==============================================
# 核心功能函数
# ==============================================

def compress_7z(
    source: str,
    output: str,
    password: Optional[str] = None,
    encryption_algorithm: str = "AES-256",
    compression_level: int = 5,
    volume_size: int = 0,
    exclude_extensions: Optional[List[str]] = None,
    threads: int = 4,
    progress_callback: Optional[Callable] = None
) -> None:
    """
    压缩文件/文件夹（支持多线程、分卷、加密）
    :param encryption_algorithm: 可选 AES-256, ChaCha20, Blowfish
    """
    filters = [{'id': py7zr.FILTER_LZMA2, 'preset': compression_level}]
    codec = _get_encryption_codec(encryption_algorithm)
    
    volume_str = f"{volume_size}M" if volume_size > 0 else None
    exclude = exclude_extensions or []

    with py7zr.SevenZipFile(
        output, 'w', password=password, filters=filters,
        codec=codec, volume=volume_str
    ) as archive:
        all_files = _get_file_list(source, exclude)
        total = len(all_files)
        
        with ThreadPoolExecutor(threads) as executor:
            with tqdm(total=total, desc="Compressing") as pbar:
                futures = []
                for file in all_files:
                    future = executor.submit(
                        archive.write, file,
                        arcname=os.path.relpath(file, source)
                    )
                    future.add_done_callback(lambda _: (pbar.update(1), progress_callback(1) if progress_callback else None))
                    futures.append(future)
                for future in futures:
                    future.result()

def extract_7z(
    archive: str,
    output_dir: str,
    password: Optional[str] = None,
    encryption_algorithm: str = "AES-256",
    threads: int = 4
) -> None:
    """解压文件（多线程支持）"""
    codec = _get_encryption_codec(encryption_algorithm)
    with py7zr.SevenZipFile(archive, 'r', password=password, codec=codec) as archive:
        archive.extractall(output_dir)

# ==============================================
# 加密相关函数
# ==============================================

def _get_encryption_codec(algorithm: str) -> List[str]:
    """获取加密算法编码"""
    algo_map = {
        "AES-256": ["AES256"],
        "ChaCha20": ["CHACHA20"],  # 需要自定义处理
        "Blowfish": ["BLOWFISH"]
    }
    return algo_map.get(algorithm, ["AES256"])

def generate_key(password: str, salt: bytes, algorithm: str) -> bytes:
    """生成加密密钥（根据算法不同长度）"""
    key_length = {
        "AES-256": 32,
        "ChaCha20": 32,
        "Blowfish": 16
    }.get(algorithm, 32)
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, key_length)

def validate_password_strength(password: str) -> bool:
    """密码强度校验：至少8字符，含大小写和数字"""
    if len(password) < 8:
        return False
    return (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password))

# ==============================================
# 文件操作函数
# ==============================================

def batch_compress(sources: List[str], output_dir: str, **kwargs) -> None:
    """批量压缩多个目录"""
    for src in sources:
        output = Path(output_dir) / f"{Path(src).name}.7z"
        compress_7z(src, str(output), **kwargs)

def split_volume(input_file: str, volume_size_mb: int) -> None:
    """分卷压缩（独立于py7zr的分卷功能）"""
    # 实现分卷逻辑（示例骨架）
    chunk_size = volume_size_mb * 1024 * 1024
    with open(input_file, 'rb') as f:
        part_num = 1
        while chunk := f.read(chunk_size):
            part_name = f"{input_file}.part{part_num:03d}"
            with open(part_name, 'wb') as part_file:
                part_file.write(chunk)
            part_num += 1

def clean_temp_files(temp_dir: str) -> None:
    """清理临时目录"""
    shutil.rmtree(temp_dir, ignore_errors=True)

# ==============================================
# 校验与元数据
# ==============================================

def calculate_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """计算文件哈希"""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_archive(archive_path: str, password: Optional[str] = None) -> bool:
    """验证压缩包完整性"""
    try:
        with py7zr.SevenZipFile(archive_path, 'r', password=password) as archive:
            return archive.testzip() is None
    except Exception:
        return False

def add_comment_to_archive(archive_path: str, comment: str) -> None:
    """添加注释到压缩包"""
    with py7zr.SevenZipFile(archive_path, 'a') as archive:
        archive.set_comment(comment)

# ==============================================
# 高级功能函数
# ==============================================

# ==============================================
# 增量压缩快照逻辑（完整实现）
# ==============================================

import json
from datetime import datetime

def create_snapshot(source: str, snapshot_file: str = ".snapshot") -> Dict:
    """创建文件快照（记录文件哈希和修改时间）"""
    snapshot = {}
    for file_path in _get_file_list(source):
        file_stat = os.stat(file_path)
        file_hash = calculate_checksum(file_path)
        snapshot[str(file_path)] = {
            "mtime": file_stat.st_mtime,
            "size": file_stat.st_size,
            "hash": file_hash
        }
    with open(snapshot_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    return snapshot

def get_modified_files(source: str, snapshot_file: str) -> List[str]:
    """对比快照获取修改文件列表"""
    current_files = _get_file_list(source)
    try:
        with open(snapshot_file, 'r') as f:
            old_snapshot = json.load(f)
    except FileNotFoundError:
        return current_files

    modified = []
    for file_path in current_files:
        file_str = str(file_path)
        file_stat = os.stat(file_str)
        
        # 文件不存在于快照中
        if file_str not in old_snapshot:
            modified.append(file_str)
            continue
            
        # 检查修改时间、大小和哈希
        old_info = old_snapshot[file_str]
        if (file_stat.st_mtime > old_info["mtime"] or
            file_stat.st_size != old_info["size"] or
            calculate_checksum(file_str) != old_info["hash"]):
            modified.append(file_str)
    
    return modified

def incremental_compress(source: str, output: str, snapshot_file: str = ".snapshot", **kwargs) -> None:
    """完整增量压缩实现"""
    modified_files = get_modified_files(source, snapshot_file)
    
    if not modified_files:
        print("没有检测到文件变更，跳过压缩")
        return
    
    # 创建临时目录仅打包修改文件
    with tempfile.TemporaryDirectory() as tmpdir:
        # 复制修改文件到临时目录保持原有结构
        for file_path in modified_files:
            rel_path = os.path.relpath(file_path, source)
            target_path = os.path.join(tmpdir, rel_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(file_path, target_path)
        
        # 执行压缩
        compress_7z(tmpdir, output, **kwargs)
        
        # 更新快照
        create_snapshot(source, snapshot_file)

# ==============================================
# 分卷压缩核心算法（完整实现）
# ==============================================

def split_volume(input_file: str, output_prefix: str, volume_size_mb: int) -> List[str]:
    """独立分卷实现（不依赖py7zr内置功能）"""
    CHUNK_SIZE = volume_size_mb * 1024 * 1024
    part_files = []
    
    with open(input_file, 'rb') as f:
        part_num = 1
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            part_name = f"{output_prefix}.part{part_num:03d}"
            with open(part_name, 'wb') as part_file:
                part_file.write(chunk)
            
            part_files.append(part_name)
            part_num += 1
    
    return part_files

def merge_volumes(input_prefix: str, output_file: str):
    """合并分卷文件"""
    part_num = 1
    with open(output_file, 'wb') as out_f:
        while True:
            part_name = f"{input_prefix}.part{part_num:03d}"
            try:
                with open(part_name, 'rb') as part_f:
                    shutil.copyfileobj(part_f, out_f)
                part_num += 1
            except FileNotFoundError:
                break

# ==============================================
# 自定义ChaCha20加密实现（完整集成）
# ==============================================

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class ChaCha20Crypto:
    def __init__(self, password: str):
        self.key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            b'salt_placeholder',  # 实际使用应生成随机salt
            100000,
            32
        )
        self.nonce = os.urandom(16)  # ChaCha20需要12或16字节nonce
    
    def encrypt(self, data: bytes) -> bytes:
        cipher = Cipher(
            algorithms.ChaCha20(self.key, self.nonce),
            mode=None,
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        return self.nonce + encryptor.update(data)
    
    def decrypt(self, data: bytes) -> bytes:
        nonce = data[:16]
        ciphertext = data[16:]
        
        cipher = Cipher(
            algorithms.ChaCha20(self.key, nonce),
            mode=None,
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext)

def chacha20_compress(source: str, output: str, password: str):
    """自定义加密压缩流程"""
    # 先压缩为临时文件
    tmp_file = output + ".tmp"
    compress_7z(source, tmp_file)
    
    # 加密压缩文件
    crypto = ChaCha20Crypto(password)
    with open(tmp_file, 'rb') as f_in:
        with open(output, 'wb') as f_out:
            chunk = f_in.read(4096)
            while chunk:
                encrypted = crypto.encrypt(chunk)
                f_out.write(encrypted)
                chunk = f_in.read(4096)
    
    # 清理临时文件
    os.remove(tmp_file)

def chacha20_extract(archive: str, output_dir: str, password: str):
    """自定义加密解压流程"""
    # 先解密为临时文件
    tmp_file = archive + ".tmp"
    crypto = ChaCha20Crypto(password)
    
    with open(archive, 'rb') as f_in:
        with open(tmp_file, 'wb') as f_out:
            chunk = f_in.read(4096 + 16)  # 包含16字节nonce
            while chunk:
                decrypted = crypto.decrypt(chunk)
                f_out.write(decrypted)
                chunk = f_in.read(4096 + 16)
    
    # 解压临时文件
    extract_7z(tmp_file, output_dir)
    os.remove(tmp_file)

# ==============================================
# 辅助函数
# ==============================================

def _get_file_list(source: str, exclude: Optional[List[str]] = None) -> List[str]:
    """获取文件列表（排除指定扩展名）"""
    exclude = exclude or []
    return [
        str(p) for p in Path(source).rglob('*')
        if p.is_file() and not any(p.suffix.lower() in ext for ext in exclude)
    ]

def _print_archive_info(archive_path: str) -> None:
    """打印压缩包信息"""
    with py7zr.SevenZipFile(archive_path, 'r') as archive:
        print(f"Archive: {archive_path}")
        print(f"Method: {archive.archiveinfo.method}")
        print(f"Solid: {archive.archiveinfo.solid}")

# ==============================================
# 命令行接口
# ==============================================


class _cil:
    """命令行接口"""
    def __init__(self, mode = False):
        if mode == False:
            self._main()

    def parser():
        return parser

    def _main(self):
        global parser
        parser = argparse.ArgumentParser(description="超级7z工具")
        subparsers = parser.add_subparsers(dest='command')

        # 压缩命令
        compress_parser = subparsers.add_parser('compress')
        compress_parser.add_argument('source', help="源文件/目录")
        compress_parser.add_argument('output', help="输出文件.7z")
        compress_parser.add_argument('-p', '--password')
        compress_parser.add_argument('-a', '--algorithm', choices=["AES-256", "ChaCha20", "Blowfish"], default="AES-256")
        compress_parser.add_argument('-l', '--level', type=int, default=5, choices=range(0,10))
        compress_parser.add_argument('-v', '--volume', type=int, help="分卷大小(MB)")
        compress_parser.add_argument('-x', '--exclude', nargs='+', help="排除扩展名 如 .tmp .log")
        compress_parser.add_argument('-t', '--threads', type=int, default=4)

        # 解压命令
        extract_parser = subparsers.add_parser('extract')
        extract_parser.add_argument('archive', help="输入文件.7z")
        extract_parser.add_argument('output_dir', help="输出目录")
        extract_parser.add_argument('-p', '--password')
        extract_parser.add_argument('-a', '--algorithm', default="AES-256")

        # 其他命令
        subparsers.add_parser('verify').add_argument('archive')
        checksum_parser = subparsers.add_parser('checksum')
        checksum_parser.add_argument('file')
        checksum_parser.add_argument('-a', '--algorithm', default="sha256")
        split_parser = subparsers.add_parser('split')
        split_parser.add_argument('input', help="输入文件")
        split_parser.add_argument('output_prefix', help="输出前缀")
        split_parser.add_argument('-s', '--size', type=int, required=True, help="分卷大小(MB)")
        
        merge_parser = subparsers.add_parser('merge')
        merge_parser.add_argument('input_prefix', help="输入前缀")
        merge_parser.add_argument('output', help="输出文件")

        args = parser.parse_args()

        try:
            if args.command == 'compress':
                if args.password and not validate_password_strength(args.password):
                    raise ValueError("密码强度不足！需要至少8位，包含大小写和数字")
                
                compress_7z(
                    args.source, args.output,
                    password=args.password,
                    encryption_algorithm=args.algorithm,
                    compression_level=args.level,
                    volume_size=args.volume,
                    exclude_extensions=args.exclude,
                    threads=args.threads
                )
                print(f"压缩完成：{args.output}")
            
            elif args.command == 'extract':
                extract_7z(
                    args.archive, args.output_dir,
                    password=args.password,
                    encryption_algorithm=args.algorithm
                )
                print(f"解压到：{args.output_dir}")
            
            elif args.command == 'verify':
                result = verify_archive(args.archive)
                print(f"完整性检查：{'通过' if result else '失败'}")

            elif args.command == 'checksum':
                print(calculate_checksum(args.file, args.algorithm))

            elif args.command == 'split':
                parts = split_volume(args.input, args.output_prefix, args.size)
                print(f"生成分卷文件：{', '.join(parts)}")
        
            elif args.command == 'merge':
                merge_volumes(args.input_prefix, args.output)
                print(f"合并完成：{args.output}")

            # 修改加密处理逻辑
            if args.algorithm == "ChaCha20":
                if args.command == 'compress':
                    chacha20_compress(args.source, args.output, args.password)
                elif args.command == 'extract':
                    chacha20_extract(args.archive, args.output_dir, args.password)

            else:
                parser.print_help()

        except Exception as e:
            print(f"错误：{e}")
            sys.exit(1)