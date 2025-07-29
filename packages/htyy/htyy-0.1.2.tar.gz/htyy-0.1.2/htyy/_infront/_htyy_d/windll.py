# windll.py
import os
import sys
import ctypes
from typing import Dict, Optional, Any

class _WindowsDLLManager:
    """Windows DLL 动态加载管理器"""
    _system_root = os.environ.get('SystemRoot', r'C:\Windows')
    _system_dir = 'System32' if sys.maxsize > 2**32 else 'SysWOW64'
    _base_path = os.path.join(_system_root, _system_dir)
    
    # 特殊 DLL 名称映射（文件名 ≠ 模块名）
    _special_mappings = {
        'winspool': 'winspool.drv',
        'vulkan': 'vulkan-1.dll',
        'xinput': 'xinput1_4.dll',
        'dinput': 'dinput8.dll',
        'msvcrt': 'msvcrt.dll',
        'gdiplus': 'gdiplus.dll',
        'd3dcompiler': 'd3dcompiler_47.dll',
        'directml': 'directml.dll'
    }
    
    # 已知问题 DLL 名单（需跳过加载）
    _blacklist = {'taskeng', 'windowsudk', 'winmd'}
    
    _cache: Dict[str, Optional[ctypes.WinDLL]] = {}

    @classmethod
    def load(cls, name: str) -> Optional[ctypes.WinDLL]:
        """智能加载 DLL"""
        if name in cls._cache:
            return cls._cache[name]
        
        if name in cls._blacklist:
            return None
        
        # 处理特殊文件名
        filename = cls._special_mappings.get(name, f"{name}.dll")
        path = os.path.join(cls._base_path, filename)
        
        # 验证文件存在性
        if not os.path.exists(path):
            return None
        
        try:
            dll = ctypes.WinDLL(path)
            cls._cache[name] = dll
            return dll
        except OSError as e:
            print(f"[WARN] Load {name} failed: {e}")
            cls._cache[name] = None
            return None
        
    _supported_dlls = [
        'user32', 'kernel32', 'gdi32', 'shell32', 'advapi32', 'ole32',
        'ws2_32', 'winmm', 'comctl32', 'shlwapi', 'version', 'oleaut32',
        'd2d1', 'dwrite', 'd3d11', 'dxgi', 'dwmapi', 'mfplat', 'msimg32',
        'wlanapi', 'winhttp', 'ncrypt', 'secur32', 'crypt32', 'iphlpapi',
        'setupapi', 'hid', 'winusb', 'cfgmgr32', 'xinput', 'dinput',
        'psapi', 'dbghelp', 'powrprof', 'wtsapi32', 'winsta', 'amsi',
        'bcrypt', 'cryptnet', 'rasapi32', 'credui', 'textinputframework',
        'twinapi', 'directml', 'vulkan', 'dxcompiler', 'mfreadwrite',
        'avrt', 'msacm32', 'dxva2', 'wmcodecdspuuid', 'sensorsapi',
        'websocket', 'ntdll', 'shcore', 'propsys', 'msctf', 'inputhost',
        'wldap32', 'dnsapi', 'odbc32', 'gdiplus', 'msvcrt', 'comdlg32',
        'winspool', 'wintrust', 'sensapi', 'imm32', 'netapi32', 'msi',
        'd3d12', 'd3dcompiler', 'wininet', 'urlmon', 'oleacc',
        'uiautomationcore', 'd3d9', 'd3d10', 'opengl32', 'glu32',
        'msimg32', 'usp10', 'uxtheme', 'winbrand', 'wtsapi32', 'wpc',
        'wer', 'wevtapi', 'wincorlib', 'wtsapi32', 'wcmapi', 'wimgapi',
        'wintypes', 'wtsapi32', 'wdsclientapi', 'wdsbp', 'wdsmc', 'wdstptc'
    ]

    @classmethod
    def list_supported_dlls(cls):
        return cls._supported_dlls

class _DLLAccessor:
    def __getattr__(self, name: str) -> ctypes.WinDLL:
        dll = _WindowsDLLManager.load(name)
        if dll is None:
            raise Exception(f"DLL '{name}' not available")
        return dll

windll = _DLLAccessor()

__author__ = "Huang Yiyi"
__version__ = "0.0.9"