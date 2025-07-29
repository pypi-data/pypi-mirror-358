import os
import sys
import subprocess
import logging
import requests
import zipfile
import tarfile
from pathlib import Path
from .config import Config

config = Config()

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(config.get('log_level'))
    
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    return logger

logger = get_logger(__name__)

def run_command(cmd, admin=False):
    """运行系统命令"""
    try:
        if admin and sys.platform == 'win32':
            cmd = f"powershell Start-Process -Verb RunAs -Wait -FilePath '{cmd[0]}' -ArgumentList '{' '.join(cmd[1:])}'"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdout, stderr = process.communicate()
        return process.returncode, stdout.decode('utf-8', 'ignore'), stderr.decode('utf-8', 'ignore')
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return -1, "", str(e)

import os
import sys
import subprocess
import logging
import requests
import zipfile
import tarfile
import certifi
from pathlib import Path
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import config

logger = logging.getLogger(__name__)

def download_file(url, dest_path):
    """下载文件并显示进度条"""
    try:
        # 创建带重试机制的会话
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        
        # 使用证书验证
        response = session.get(url, stream=True, verify=certifi.where())
        response.raise_for_status()
        
        # 获取文件总大小（字节）
        total_size = int(response.headers.get('content-length', 0))
        
        # 创建进度条
        progress_bar = tqdm(
            total=total_size, 
            unit='iB', 
            unit_scale=True, 
            desc=f"下载 {os.path.basename(dest_path)}",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
        )
        
        # 分块写入文件
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # 过滤掉保持连接的新块
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        # 关闭进度条
        progress_bar.close()
        
        # 验证文件大小
        if total_size != 0 and progress_bar.n != total_size:
            logger.error("下载不完整")
            return False
        
        return True
    except Exception as e:
        logger.error(f"下载失败: {e}")
        logger.info("尝试使用不验证证书的方式下载...")
        
        # 尝试不使用证书验证
        try:
            session = requests.Session()
            retry_strategy = Retry(total=3, backoff_factor=1)
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            
            response = session.get(url, stream=True, verify=False)
            response.raise_for_status()
            
            # 获取文件总大小（字节）
            total_size = int(response.headers.get('content-length', 0))
            
            # 创建进度条
            progress_bar = tqdm(
                total=total_size, 
                unit='iB', 
                unit_scale=True, 
                desc=f"备用下载 {os.path.basename(dest_path)}",
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'
            )
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            progress_bar.close()
            
            # 验证文件大小
            if total_size != 0 and progress_bar.n != total_size:
                logger.error("下载不完整")
                return False
            
            return True
        except Exception as e2:
            logger.error(f"备用下载方式失败: {e2}")
            return False

def extract_archive(file_path, extract_dir):
    """解压文件"""
    try:
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            with tarfile.open(file_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
        return True
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return False

def get_binary_dir():
    """获取二进制文件目录"""
    module_dir = Path(__file__).parent.parent
    bin_dir = module_dir / 'bin' / config.system_platform / config.architecture
    bin_dir.mkdir(parents=True, exist_ok=True)
    return bin_dir

def get_vlmcsd_path():
    """获取vlmcsd路径"""
    config_path = config.get('vlmcsd_path')
    if config_path and os.path.exists(config_path):
        return config_path
    
    bin_dir = get_binary_dir()
    
    # 尝试查找已存在的二进制文件
    binary_name = "vlmcsd.exe" if sys.platform == "win32" else "vlmcsd"
    binary_path = bin_dir / binary_name
    
    if binary_path.exists():
        return str(binary_path)
    
    # 如果没有找到，尝试下载
    if not download_vlmcsd():
        return None
    
    return str(binary_path)

def download_vlmcsd():
    """下载vlmcsd二进制文件"""
    logger.info("Downloading vlmcsd binary...")
    
    base_url = "https://github.com/Wind4/vlmcsd/releases/download/svn1113/binaries.tar.gz"
    temp_dir = Path.home() / ".kms_activator" / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    archive_path = temp_dir / "binaries.tar.gz"
    
    if not download_file(base_url, archive_path):
        return False
    
    if not extract_archive(archive_path, temp_dir):
        return False
    
    # 找到对应的二进制文件
    bin_dir = get_binary_dir()
    platform_name = config.system_platform
    arch_name = config.architecture
    
    # 在解压目录中查找对应平台的二进制文件
    source_dir = temp_dir / "binaries" / platform_name.capitalize()
    if not source_dir.exists():
        logger.error(f"Unsupported platform: {platform_name}")
        return False
    
    # 根据架构选择文件
    if platform_name == "windows":
        binary_name = f"vlmcsd-{arch_name}.exe"
    else:
        binary_name = f"vlmcsd-{arch_name}-musl-static"
    
    source_path = None
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file == binary_name:
                source_path = Path(root) / file
                break
    
    if not source_path:
        logger.error(f"Binary not found: {binary_name}")
        return False
    
    # 复制到目标目录
    target_path = bin_dir / ("vlmcsd.exe" if platform_name == "windows" else "vlmcsd")
    source_path.rename(target_path)
    
    # 设置可执行权限
    if platform_name != "windows":
        os.chmod(target_path, 0o755)
    
    # 更新配置
    config.set('vlmcsd_path', str(target_path))
    
    logger.info(f"vlmcsd downloaded to {target_path}")
    return True