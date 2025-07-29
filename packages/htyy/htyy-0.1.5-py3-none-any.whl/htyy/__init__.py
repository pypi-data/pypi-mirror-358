"""
 htyy
~~~~~~
Version: 0.1.5
"""

from . import client, modules
from . import reponse
from . import extensions
from . import request
from . import version
from . import message
from . import _path
from .windll import windll, platform
from .pyos import *
from . import pyos, hpyy
from ._infront._htyy_d import (
    combination, cos, cosh, cot, ComplexNumber,
    AdminPrivilegeChecker, exp, sha1, sha224,
    sha256, sha384, sha3_256, sha3_384, sha3_512,
    sha512, shake_128, shake_256, sin, sinh, sqrt,
    factorial, floor, blake2b, blake2s, absolute_value,
    tan, tanh, pi, power, md5, ln, log10, cmd, HF,
    WithHtyy, HtyySet, HtNone, HLen
)
from . import websys, winp
from . import _h7z as h7z, _system as temsys
from . import gui
import logging, os, winreg
from pathlib import Path
import warnings

class HtyyWarning(Warning):
    pass

class HtyyTqdmWarning(HtyyWarning):
    pass

try:
    import tqdm
except:
    warnings.warn(
        "The tqdm library is not detected and some features may be limited. Please run 'pip install tqdm' to install.",
        HtyyTqdmWarning,
        stacklevel=2
    )

__version__ = version.__version__

import miniaudio
import pyaudio
import threading
import time
import numpy as np

class Music:
    def __init__(self, file_path, play_time=-1):
        self.file_path = file_path
        self.play_time = play_time
        self._running = False
        self.audio_thread = None
        self._load_audio()  # 加载音频
        self.play()

    def _load_audio(self):
        """使用 miniaudio 加载音频"""
        try:
            # 解码音频文件（默认输出为 16 位整数）
            decoded = miniaudio.decode_file(self.file_path)
            self.sample_rate = decoded.sample_rate
            self.channels = decoded.nchannels
            # 将数据转换为 numpy 数组（int16）
            self.audio_data = np.frombuffer(decoded.samples, dtype=np.int16)
        except Exception as e:
            raise ValueError(f"Failed to load audio:{e}")

    def _play_audio(self):
        """核心播放逻辑"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,  # 指定 16 位整数格式
            channels=self.channels,
            rate=self.sample_rate,
            output=True
        )

        self._running = True
        start_time = time.time()
        pos = 0
        chunk_size = 1024  # 每次写入的帧数

        while self._running and pos < len(self.audio_data):
            if self.play_time > 0 and (time.time() - start_time) >= self.play_time:
                break

            end_pos = pos + chunk_size * self.channels  # 注意：每个帧包含多个通道的数据
            chunk = self.audio_data[pos:end_pos]
            stream.write(chunk.tobytes())
            pos = end_pos

        stream.stop_stream()
        stream.close()
        p.terminate()

    def play(self):
        if not self._running:
            self.audio_thread = threading.Thread(target=self._play_audio)
            self.audio_thread.start()

    def stop(self):
        self._running = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()

from PIL import Image

class ImageConversionError(Exception):
    """自定义图像转换异常"""
    pass

class ImageConversion:
    SUPPORTED_FORMATS = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "bmp": "BMP",
        "webp": "WEBP",
        "gif": "GIF",
        "tiff": "TIFF"
    }

    def __init__(self, input_path: str, output_path: str, **kwargs):
        """
        初始化图像转换器
        :param input_path:  输入图像路径（如 "D:/input.jpg"）
        :param output_path: 输出图像路径（如 "D:/output.png"）
        :param kwargs:      可选参数（如 quality=85, optimize=True）
        """
        self.input_path = Path(input_path).resolve()
        self.output_path = Path(output_path).resolve()
        self.convert_params = kwargs  # 转换参数（如质量、优化选项）
        self._validate_paths()
        logging.basicConfig(level=logging.INFO)

    def _validate_paths(self):
        """验证输入输出路径合法性"""
        # 输入文件检查
        if not self.input_path.exists():
            raise FileNotFoundError(f"The input file does not exist: {self.input_path}")
        
        # 输入格式支持性检查
        input_ext = self.input_path.suffix.lower()[1:]
        if input_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported input formats: .{input_ext}")

        # 输出目录写入权限检查
        output_dir = self.output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(str(output_dir), os.W_OK):
            raise PermissionError(f"No write permissions: {output_dir}")

        # 输出格式支持性检查
        output_ext = self.output_path.suffix.lower()[1:]
        if output_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported output formats: .{output_ext}")

    def _get_save_params(self) -> dict:
        """根据输出格式生成保存参数"""
        output_ext = self.output_path.suffix.lower()[1:]
        params = self.convert_params.copy()

        # 格式特定参数（示例：JPEG 质量、PNG 压缩）
        if output_ext in ["jpg", "jpeg"]:
            params.setdefault("quality", 90)  # 默认 JPEG 质量 90%
        elif output_ext == "webp":
            params.setdefault("quality", 80)  # 默认 WEBP 质量 80%
        elif output_ext == "png":
            params.setdefault("compress_level", 6)  # PNG 压缩级别

        return params

    def convert(self):
        """执行图像格式转换"""
        try:
            # 打开输入图像
            with Image.open(self.input_path) as img:
                # 转换 RGBA 格式处理（如 PNG 转 JPEG 需移除透明度）
                if img.mode in ("RGBA", "LA") and self.output_path.suffix.lower() in [".jpg", ".jpeg"]:
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])  # 移除透明度
                    img = background

                # 保存为输出格式
                img.save(
                    self.output_path,
                    format=self.SUPPORTED_FORMATS[self.output_path.suffix.lower()[1:]],
                    **self._get_save_params()
                )
            
            logging.info(f"The conversion was successful: {self.output_path}")

        except IOError as e:
            error_msg = f"Image processing failed: {str(e)}"
            logging.error(error_msg)
            raise ImageConversionError(error_msg)
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            raise

"""
if __name__ == "__main__":
    try:
        converter = VideoConversion(
            input_path="D:/test_video.mp4",
            output_path="D:/output/test_audio.wav"
        )
        converter.convert()
    except Exception as e:
        print(f"转换失败: {str(e)}")
        sys.exit(1)
"""

path = _path
htyy = __file__
import sys
_names = sys.builtin_module_names

if _names == "nt":
    name = "win32"

elif _names == "posix":
    name = "posix"

else:
    name = _names

from ._a import compile_c_to_pyd
_ = name

import os
import subprocess
import tempfile
import datetime
import platform
from typing import Union, Tuple, Optional

class PowerShellFileTimeSetter:
    def __init__(
        self, 
        file_path: str,
        creation_time: Optional[Union[datetime.datetime, str]] = None,
        last_write_time: Optional[Union[datetime.datetime, str]] = None,
        last_access_time: Optional[Union[datetime.datetime, str]] = None,
        default_time: Union[datetime.datetime, str] = datetime.datetime(1980, 1, 1)
    ):
        """
        初始化文件时间设置器
        
        参数:
            file_path (str): 要修改的文件路径
            creation_time (datetime/str): 文件的创建时间，可以是datetime对象或"YYYY-MM-DD HH:MM:SS"字符串
            last_write_time (datetime/str): 文件的修改时间
            last_access_time (datetime/str): 文件的访问时间
            default_time (datetime/str): 默认时间（当其他时间未提供或无效时使用）
        
        # 示例1：在初始化时设置所有时间
        print("示例1: 在初始化时设置所有时间")
        setter1 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            creation_time="1111-11-11 11:11:11",
            last_write_time="2222-02-22 22:22:22",
            last_access_time="3333-03-33 03:33:33"  # 这个时间无效，将使用默认时间
        )
        print(setter1)
        success, output = setter1.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        
        # 示例2：使用默认时间
        print("\n示例2: 使用默认时间")
        setter2 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            default_time="1999-12-31 23:59:59"
        )
        print(setter2)
        success, output = setter2.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        
        # 示例3：使用set_all_times_to方法
        print("\n示例3: 使用set_all_times_to方法")
        setter3 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            default_time="2000-01-01"
        )
        setter3.set_all_times_to("2025-06-10 12:00:00")
        print(setter3)
        success, output = setter3.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        
        # 示例4：使用datetime对象
        print("\n示例4: 使用datetime对象")
        custom_time = datetime.datetime(2100, 12, 31, 23, 59, 59)
        setter4 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            creation_time=custom_time,
            last_write_time=custom_time
        )
        print(setter4)
        success, output = setter4.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        """
        self.file_path = file_path
        self.default_time = self._parse_time(default_time) if isinstance(default_time, str) else default_time
        
        # 解析时间参数
        self.creation_time = self._parse_time(creation_time) if creation_time else self.default_time
        self.last_write_time = self._parse_time(last_write_time) if last_write_time else self.default_time
        self.last_access_time = self._parse_time(last_access_time) if last_access_time else self.default_time
        
        # PowerShell相关变量
        self.temp_script = None
        self.execution_policy_bypassed = False
        self.original_execution_policy = None
        self.is_windows = platform.system() == "Windows"
        
        # 确保文件存在
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                f.write("Temporary file for time setting")
    
    def _parse_time(self, time_input: Union[datetime.datetime, str]) -> datetime.datetime:
        """解析时间输入（支持datetime对象或字符串）"""
        if isinstance(time_input, datetime.datetime):
            return time_input
        
        try:
            # 尝试解析带时间的字符串格式
            return datetime.datetime.strptime(time_input, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # 尝试解析仅日期的字符串格式
                return datetime.datetime.strptime(time_input, "%Y-%m-%d")
            except ValueError:
                # 尝试解析自定义格式
                try:
                    return datetime.datetime.strptime(time_input, "%Y/%m/%d %H:%M:%S")
                except:
                    # 所有尝试失败，使用默认时间
                    return self.default_time
    
    def _escape_path(self, path: str) -> str:
        """转义路径中的特殊字符"""
        return path.replace("'", "''").replace("&", "`&")
    
    def _create_powershell_script(self) -> str:
        """创建 PowerShell 脚本内容"""
        escaped_path = self._escape_path(self.file_path)
        
        script = f"""
# 设置文件时间属性
$file = '{escaped_path}'

# 检查文件是否存在
if (-not (Test-Path -Path $file -PathType Leaf)) {{
    Write-Host "错误: 文件 '$file' 不存在" -ForegroundColor Red
    exit 1
}}

# 创建时间对象
try {{
    $creationDate = [DateTime]::new({self.creation_time.year}, {self.creation_time.month}, {self.creation_time.day}, {self.creation_time.hour}, {self.creation_time.minute}, {self.creation_time.second})
    $writeDate = [DateTime]::new({self.last_write_time.year}, {self.last_write_time.month}, {self.last_write_time.day}, {self.last_write_time.hour}, {self.last_write_time.minute}, {self.last_write_time.second})
    $accessDate = [DateTime]::new({self.last_access_time.year}, {self.last_access_time.month}, {self.last_access_time.day}, {self.last_access_time.hour}, {self.last_access_time.minute}, {self.last_access_time.second})
    
    Write-Host "目标创建时间: $creationDate"
    Write-Host "目标修改时间: $writeDate"
    Write-Host "目标访问时间: $accessDate"
}}
catch {{
    Write-Host "创建日期对象失败: $_" -ForegroundColor Red
    exit 2
}}

# 设置文件时间属性
try {{
    Set-ItemProperty -Path $file -Name CreationTime -Value $creationDate -ErrorAction Stop
    Set-ItemProperty -Path $file -Name LastWriteTime -Value $writeDate -ErrorAction Stop
    Set-ItemProperty -Path $file -Name LastAccessTime -Value $accessDate -ErrorAction Stop
    
    Write-Host "文件时间属性已成功修改!" -ForegroundColor Green
    exit 0
}}
catch {{
    Write-Host "修改文件时间失败: $_" -ForegroundColor Red
    exit 3
}}
"""
        return script
    
    def _save_script_to_tempfile(self, script_content: str) -> str:
        """保存脚本到临时文件"""
        with tempfile.NamedTemporaryFile(suffix='.ps1', delete=False) as temp:
            temp.write(script_content.encode('utf-8'))
            self.temp_script = temp.name
        return self.temp_script
    
    def _get_execution_policy(self) -> Optional[str]:
        """获取当前执行策略"""
        if not self.is_windows:
            return None
            
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-ExecutionPolicy'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except:
            return None
    
    def _set_execution_policy(self, policy: str) -> bool:
        """设置执行策略"""
        if not self.is_windows:
            return False
            
        try:
            subprocess.run(
                ['powershell', '-Command', f'Set-ExecutionPolicy {policy} -Scope CurrentUser -Force'],
                check=True
            )
            return True
        except:
            return False
    
    def _bypass_execution_policy(self) -> bool:
        """临时绕过执行策略限制"""
        if not self.is_windows:
            return False
            
        self.original_execution_policy = self._get_execution_policy()
        if self.original_execution_policy:
            # 临时设置为Bypass
            if self._set_execution_policy('Bypass'):
                self.execution_policy_bypassed = True
                return True
        return False
    
    def _restore_execution_policy(self) -> bool:
        """恢复原始执行策略"""
        if not self.is_windows or not self.execution_policy_bypassed or not self.original_execution_policy:
            return False
            
        return self._set_execution_policy(self.original_execution_policy)
    
    def apply(self) -> Tuple[bool, str]:
        """
        应用设置的时间到文件
        
        返回:
            tuple: (success: bool, output: str)
        """
        if not self.is_windows:
            return False, "此功能仅支持Windows系统"
        
        # 创建PowerShell脚本
        ps_script = self._create_powershell_script()
        script_path = self._save_script_to_tempfile(ps_script)
        
        # 尝试绕过执行策略
        self._bypass_execution_policy()
        
        try:
            # 运行PowerShell脚本
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                capture_output=True, text=True, check=True
            )
            success = result.returncode == 0
            return success, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"执行错误: {e.stderr}"
        finally:
            # 清理临时文件
            if self.temp_script and os.path.exists(self.temp_script):
                os.remove(self.temp_script)
            
            # 恢复执行策略
            self._restore_execution_policy()
    
    def set_all_times_to(self, target_time: Union[datetime.datetime, str]) -> None:
        """
        设置所有时间属性为同一时间
        
        参数:
            target_time (datetime/str): 目标时间
        """
        parsed_time = self._parse_time(target_time) if isinstance(target_time, str) else target_time
        self.creation_time = parsed_time
        self.last_write_time = parsed_time
        self.last_access_time = parsed_time
    
    def __str__(self) -> str:
        """返回类的字符串表示"""
        return (
            f"FileTimeSetter for: {self.file_path}\n"
            f"  Creation Time: {self.creation_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  Last Write Time: {self.last_write_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  Last Access Time: {self.last_access_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    def __del__(self):
        """析构函数，确保清理"""
        if self.temp_script and os.path.exists(self.temp_script):
            os.remove(self.temp_script)
        if self.execution_policy_bypassed:
            self._restore_execution_policy()

class psfts:
    def __init__(
        self, 
        file_path: str,
        creation_time: Optional[Union[datetime.datetime, str]] = None,
        last_write_time: Optional[Union[datetime.datetime, str]] = None,
        last_access_time: Optional[Union[datetime.datetime, str]] = None,
        default_time: Union[datetime.datetime, str] = datetime.datetime(1980, 1, 1)
    ):
        """
        初始化文件时间设置器
        
        参数:
            file_path (str): 要修改的文件路径
            creation_time (datetime/str): 文件的创建时间，可以是datetime对象或"YYYY-MM-DD HH:MM:SS"字符串
            last_write_time (datetime/str): 文件的修改时间
            last_access_time (datetime/str): 文件的访问时间
            default_time (datetime/str): 默认时间（当其他时间未提供或无效时使用）
        
        # 示例1：在初始化时设置所有时间
        print("示例1: 在初始化时设置所有时间")
        setter1 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            creation_time="1111-11-11 11:11:11",
            last_write_time="2222-02-22 22:22:22",
            last_access_time="3333-03-33 03:33:33"  # 这个时间无效，将使用默认时间
        )
        print(setter1)
        success, output = setter1.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        
        # 示例2：使用默认时间
        print("\n示例2: 使用默认时间")
        setter2 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            default_time="1999-12-31 23:59:59"
        )
        print(setter2)
        success, output = setter2.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        
        # 示例3：使用set_all_times_to方法
        print("\n示例3: 使用set_all_times_to方法")
        setter3 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            default_time="2000-01-01"
        )
        setter3.set_all_times_to("2025-06-10 12:00:00")
        print(setter3)
        success, output = setter3.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        
        # 示例4：使用datetime对象
        print("\n示例4: 使用datetime对象")
        custom_time = datetime.datetime(2100, 12, 31, 23, 59, 59)
        setter4 = PowerShellFileTimeSetter(
            file_path="F:\\hyy&\\pip.txt",
            creation_time=custom_time,
            last_write_time=custom_time
        )
        print(setter4)
        success, output = setter4.apply()
        print("操作成功:", success)
        print("输出结果:", output)
        """
        self.file_path = file_path
        self.default_time = self._parse_time(default_time) if isinstance(default_time, str) else default_time
        
        # 解析时间参数
        self.creation_time = self._parse_time(creation_time) if creation_time else self.default_time
        self.last_write_time = self._parse_time(last_write_time) if last_write_time else self.default_time
        self.last_access_time = self._parse_time(last_access_time) if last_access_time else self.default_time
        
        # PowerShell相关变量
        self.temp_script = None
        self.execution_policy_bypassed = False
        self.original_execution_policy = None
        self.is_windows = platform.system() == "Windows"
        
        # 确保文件存在
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                f.write("Temporary file for time setting")
    
    def _parse_time(self, time_input: Union[datetime.datetime, str]) -> datetime.datetime:
        """解析时间输入（支持datetime对象或字符串）"""
        if isinstance(time_input, datetime.datetime):
            return time_input
        
        try:
            # 尝试解析带时间的字符串格式
            return datetime.datetime.strptime(time_input, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # 尝试解析仅日期的字符串格式
                return datetime.datetime.strptime(time_input, "%Y-%m-%d")
            except ValueError:
                # 尝试解析自定义格式
                try:
                    return datetime.datetime.strptime(time_input, "%Y/%m/%d %H:%M:%S")
                except:
                    # 所有尝试失败，使用默认时间
                    return self.default_time
    
    def _escape_path(self, path: str) -> str:
        """转义路径中的特殊字符"""
        return path.replace("'", "''").replace("&", "`&")
    
    def _create_powershell_script(self) -> str:
        """创建 PowerShell 脚本内容"""
        escaped_path = self._escape_path(self.file_path)
        
        script = f"""
# 设置文件时间属性
$file = '{escaped_path}'

# 检查文件是否存在
if (-not (Test-Path -Path $file -PathType Leaf)) {{
    Write-Host "错误: 文件 '$file' 不存在" -ForegroundColor Red
    exit 1
}}

# 创建时间对象
try {{
    $creationDate = [DateTime]::new({self.creation_time.year}, {self.creation_time.month}, {self.creation_time.day}, {self.creation_time.hour}, {self.creation_time.minute}, {self.creation_time.second})
    $writeDate = [DateTime]::new({self.last_write_time.year}, {self.last_write_time.month}, {self.last_write_time.day}, {self.last_write_time.hour}, {self.last_write_time.minute}, {self.last_write_time.second})
    $accessDate = [DateTime]::new({self.last_access_time.year}, {self.last_access_time.month}, {self.last_access_time.day}, {self.last_access_time.hour}, {self.last_access_time.minute}, {self.last_access_time.second})
    
    Write-Host "目标创建时间: $creationDate"
    Write-Host "目标修改时间: $writeDate"
    Write-Host "目标访问时间: $accessDate"
}}
catch {{
    Write-Host "创建日期对象失败: $_" -ForegroundColor Red
    exit 2
}}

# 设置文件时间属性
try {{
    Set-ItemProperty -Path $file -Name CreationTime -Value $creationDate -ErrorAction Stop
    Set-ItemProperty -Path $file -Name LastWriteTime -Value $writeDate -ErrorAction Stop
    Set-ItemProperty -Path $file -Name LastAccessTime -Value $accessDate -ErrorAction Stop
    
    Write-Host "文件时间属性已成功修改!" -ForegroundColor Green
    exit 0
}}
catch {{
    Write-Host "修改文件时间失败: $_" -ForegroundColor Red
    exit 3
}}
"""
        return script
    
    def _save_script_to_tempfile(self, script_content: str) -> str:
        """保存脚本到临时文件"""
        with tempfile.NamedTemporaryFile(suffix='.ps1', delete=False) as temp:
            temp.write(script_content.encode('utf-8'))
            self.temp_script = temp.name
        return self.temp_script
    
    def _get_execution_policy(self) -> Optional[str]:
        """获取当前执行策略"""
        if not self.is_windows:
            return None
            
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-ExecutionPolicy'],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except:
            return None
    
    def _set_execution_policy(self, policy: str) -> bool:
        """设置执行策略"""
        if not self.is_windows:
            return False
            
        try:
            subprocess.run(
                ['powershell', '-Command', f'Set-ExecutionPolicy {policy} -Scope CurrentUser -Force'],
                check=True
            )
            return True
        except:
            return False
    
    def _bypass_execution_policy(self) -> bool:
        """临时绕过执行策略限制"""
        if not self.is_windows:
            return False
            
        self.original_execution_policy = self._get_execution_policy()
        if self.original_execution_policy:
            # 临时设置为Bypass
            if self._set_execution_policy('Bypass'):
                self.execution_policy_bypassed = True
                return True
        return False
    
    def _restore_execution_policy(self) -> bool:
        """恢复原始执行策略"""
        if not self.is_windows or not self.execution_policy_bypassed or not self.original_execution_policy:
            return False
            
        return self._set_execution_policy(self.original_execution_policy)
    
    def apply(self) -> Tuple[bool, str]:
        """
        应用设置的时间到文件
        
        返回:
            tuple: (success: bool, output: str)
        """
        if not self.is_windows:
            return False, "此功能仅支持Windows系统"
        
        # 创建PowerShell脚本
        ps_script = self._create_powershell_script()
        script_path = self._save_script_to_tempfile(ps_script)
        
        # 尝试绕过执行策略
        self._bypass_execution_policy()
        
        try:
            # 运行PowerShell脚本
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                capture_output=True, text=True, check=True
            )
            success = result.returncode == 0
            return success, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"执行错误: {e.stderr}"
        finally:
            # 清理临时文件
            if self.temp_script and os.path.exists(self.temp_script):
                os.remove(self.temp_script)
            
            # 恢复执行策略
            self._restore_execution_policy()
    
    def set_all_times_to(self, target_time: Union[datetime.datetime, str]) -> None:
        """
        设置所有时间属性为同一时间
        
        参数:
            target_time (datetime/str): 目标时间
        """
        parsed_time = self._parse_time(target_time) if isinstance(target_time, str) else target_time
        self.creation_time = parsed_time
        self.last_write_time = parsed_time
        self.last_access_time = parsed_time
    
    def __str__(self) -> str:
        """返回类的字符串表示"""
        return (
            f"FileTimeSetter for: {self.file_path}\n"
            f"  Creation Time: {self.creation_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  Last Write Time: {self.last_write_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  Last Access Time: {self.last_access_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    def __del__(self):
        """析构函数，确保清理"""
        if self.temp_script and os.path.exists(self.temp_script):
            os.remove(self.temp_script)
        if self.execution_policy_bypassed:
            self._restore_execution_policy()

class FileAssociation:
    """根据一个文件路径来确认所关联的exe文件，最后结果存储在exe_path里"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.extension = os.path.splitext(file_path)[1].lower()  # 获取文件扩展名
        self.exe_path = self._get_associated_exe()
    
    def _get_associated_exe(self):
        """获取文件关联的exe路径"""
        # 非Windows系统不支持
        if sys.platform != 'win32':
            raise NotImplementedError("File association only supported on Windows")
        
        # 无扩展名的文件无法关联
        if not self.extension:
            return None
        
        try:
            # 1. 获取文件类型
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, self.extension) as key:
                file_type = winreg.QueryValue(key, None)
            
            # 2. 获取关联的应用程序命令
            command_path = f"{file_type}\\shell\\open\\command"
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, command_path) as key:
                command = winreg.QueryValue(key, None)
            
            # 3. 清理命令字符串
            exe_path = self._clean_command(command)
            return exe_path
        
        except WindowsError:
            return None  # 找不到关联程序
    
    def _clean_command(self, command):
        """从命令行字符串中提取干净的exe路径"""
        # 去除环境变量
        expanded = os.path.expandvars(command)
        
        # 提取第一个可执行文件部分
        if expanded.startswith('"'):
            end = expanded.find('"', 1)
            exe_path = expanded[1:end] if end != -1 else expanded.split()[0]
        else:
            exe_path = expanded.split()[0]
        
        return exe_path
    
class fs:
    """根据一个文件路径来确认所关联的exe文件，最后结果存储在exe_path里"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.extension = os.path.splitext(file_path)[1].lower()  # 获取文件扩展名
        self.exe_path = self._get_associated_exe()
    
    def _get_associated_exe(self):
        """获取文件关联的exe路径"""
        # 非Windows系统不支持
        if sys.platform != 'win32':
            raise NotImplementedError("File association only supported on Windows")
        
        # 无扩展名的文件无法关联
        if not self.extension:
            return None
        
        try:
            # 1. 获取文件类型
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, self.extension) as key:
                file_type = winreg.QueryValue(key, None)
            
            # 2. 获取关联的应用程序命令
            command_path = f"{file_type}\\shell\\open\\command"
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, command_path) as key:
                command = winreg.QueryValue(key, None)
            
            # 3. 清理命令字符串
            exe_path = self._clean_command(command)
            return exe_path
        
        except WindowsError:
            return None  # 找不到关联程序
    
    def _clean_command(self, command):
        """从命令行字符串中提取干净的exe路径"""
        # 去除环境变量
        expanded = os.path.expandvars(command)
        
        # 提取第一个可执行文件部分
        if expanded.startswith('"'):
            end = expanded.find('"', 1)
            exe_path = expanded[1:end] if end != -1 else expanded.split()[0]
        else:
            exe_path = expanded.split()[0]
        
        return exe_path

if __name__ == "__main__":
    message.showinfo("Title","Message\nmsg")
    response = request.get('https://codinghou.cn', timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text[:200]}...")
    if not path.exists("PATH"):
        pass

    else:
        print(htyy)

    if platform == "windows":
        print("system is windows.")

    elif platform == "linux":
        print("system is linux.")
    
    elif platform == "darwin":
        print("system is macos.")

    else:
        print(platform)
    