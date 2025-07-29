"""This is htyy Path"""

import sys, os
import ctypes, subprocess

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
GetFileAttributesW = kernel32.GetFileAttributesW

def exists(path):
    if sys.platform.startswith('win32'):
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        GetFileAttributesW = kernel32.GetFileAttributesW
        GetFileAttributesW.argtypes = [ctypes.c_wchar_p]
        GetFileAttributesW.restype = ctypes.c_uint
        INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
        return GetFileAttributesW(path) != INVALID_FILE_ATTRIBUTES
    else:
        libc = ctypes.CDLL(None)
        stat = libc.stat
        stat.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
        stat.restype = ctypes.c_int
        return stat(path.encode(), None) == 0
    
def expanduser(path):
    if not path.startswith('~'):
        return path
    
    if sys.platform.startswith('win32'):
        env_var = 'USERPROFILE'
    else:
        env_var = 'HOME'
    
    # 使用 ctypes 获取环境变量
    libc = ctypes.CDLL(None)
    getenv = libc.getenv
    getenv.argtypes = [ctypes.c_char_p]
    getenv.restype = ctypes.c_char_p
    home = getenv(env_var.encode())
    
    if not home:
        return path
    
    home = home.decode()
    return home + path[1:] if len(path) > 1 else home

def isfile(path):
    if sys.platform.startswith('win32'):
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        GetFileAttributesW = kernel32.GetFileAttributesW
        attr = GetFileAttributesW(path)
        return attr != 0xFFFFFFFF and not (attr & 0x10)
    else:
        class Stat(ctypes.Structure):
            _fields_ = [("st_mode", ctypes.c_uint)]
        libc = ctypes.CDLL(None)
        stat = libc.stat
        stat.argtypes = [ctypes.c_char_p, ctypes.POINTER(Stat)]
        stat.restype = ctypes.c_int
        buf = Stat()
        return stat(path.encode(), ctypes.byref(buf)) == 0 and (buf.st_mode & 0o170000) == 0o100000

def isdir(path):
    if sys.platform.startswith('win32'):
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        GetFileAttributesW = kernel32.GetFileAttributesW
        attr = GetFileAttributesW(path)
        return attr != 0xFFFFFFFF and (attr & 0x10)
    else:
        class Stat(ctypes.Structure):
            _fields_ = [("st_mode", ctypes.c_uint)]
        libc = ctypes.CDLL(None)
        stat = libc.stat
        stat.argtypes = [ctypes.c_char_p, ctypes.POINTER(Stat)]
        stat.restype = ctypes.c_int
        buf = Stat()
        return stat(path.encode(), ctypes.byref(buf)) == 0 and (buf.st_mode & 0o170000) == 0o040000
    
def join(*paths):
    if not paths:
        return ''
    
    sep = '\\' if sys.platform.startswith('win32') else '/'
    result = []
    for path in paths:
        if not path:
            continue
        if result:
            last = result[-1]
            if last.endswith(sep):
                result.append(path.lstrip(sep))
            else:
                result.append(sep + path.lstrip(sep))
        else:
            result.append(path)
    
    full_path = ''.join(result)
    parts = []
    for part in full_path.split(sep):
        if part == '..':
            if parts:
                parts.pop()
        elif part != '.' and part:
            parts.append(part)
    return sep + sep.join(parts) if full_path.startswith(sep) else sep.join(parts)

import sys
import ctypes
from ctypes import wintypes
import time

class StatResult:
    """模拟 os.stat_result 的类，提供文件属性"""
    def __init__(self, st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid,
                 st_size, st_atime, st_mtime, st_ctime):
        self.st_mode = st_mode
        self.st_ino = st_ino
        self.st_dev = st_dev
        self.st_nlink = st_nlink
        self.st_uid = st_uid
        self.st_gid = st_gid
        self.st_size = st_size
        self.st_atime = st_atime
        self.st_mtime = st_mtime
        self.st_ctime = st_ctime

    def __getitem__(self, index):
        return (
            self.st_mode, self.st_ino, self.st_dev, self.st_nlink,
            self.st_uid, self.st_gid, self.st_size, self.st_atime,
            self.st_mtime, self.st_ctime
        )[index]

def stat(path):
    if sys.platform.startswith('win32'):
        return _stat_windows(path)
    else:
        return _stat_unix(path)

# ------------------------- Windows 实现 -------------------------
def _filetime_to_unix(ft):
    """将 Windows FILETIME 转换为 Unix 时间戳（秒）"""
    total = (ft.dwHighDateTime << 32) + ft.dwLowDateTime
    total -= 116444736000000000  # 1601-01-01 到 1970-01-01 的间隔
    return total / 10000000.0

def _stat_windows(path):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    path_w = ctypes.c_wchar_p(path)

    # 打开文件句柄以获取信息
    handle = kernel32.CreateFileW(
        path_w,
        0x80000000,  # GENERIC_READ
        1,            # FILE_SHARE_READ
        None,
        3,            # OPEN_EXISTING
        0x02000000,   # FILE_FLAG_BACKUP_SEMANTICS（允许目录操作）
        0
    )
    if handle == wintypes.HANDLE(-1).value:
        raise FileNotFoundError(f"文件不存在: {path}")

    try:
        # 获取文件信息
        file_info = _BY_HANDLE_FILE_INFORMATION()
        if not kernel32.GetFileInformationByHandle(handle, ctypes.byref(file_info)):
            raise OSError("无法获取文件信息")

        # 获取文件时间
        creation_time = _FILETIME()
        access_time = _FILETIME()
        write_time = _FILETIME()
        kernel32.GetFileTime(handle, creation_time, access_time, write_time)

        # 文件大小（64 位）
        st_size = (file_info.nFileSizeHigh << 32) | file_info.nFileSizeLow

        # 模拟 st_mode
        st_mode = 0
        if file_info.dwFileAttributes & 0x10:  # 目录
            st_mode |= 0o040000
        else:
            st_mode |= 0o100000
        if file_info.dwFileAttributes & 0x1:   # 只读
            st_mode |= 0o444
        else:
            st_mode |= 0o666

        # 处理符号链接（需要额外检查）
        if file_info.dwFileAttributes & 0x400:  # 重解析点
            st_mode = 0o120000  # S_IFLNK

        return StatResult(
            st_mode=st_mode,
            st_ino=(file_info.nFileIndexHigh << 32) | file_info.nFileIndexLow,
            st_dev=file_info.dwVolumeSerialNumber,
            st_nlink=file_info.nNumberOfLinks,
            st_uid=0,  # Windows 无 UID/GID
            st_gid=0,
            st_size=st_size,
            st_atime=_filetime_to_unix(access_time),
            st_mtime=_filetime_to_unix(write_time),
            st_ctime=_filetime_to_unix(creation_time)
        )
    finally:
        kernel32.CloseHandle(handle)

# Windows 结构体定义
class _FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", wintypes.DWORD),
                ("dwHighDateTime", wintypes.DWORD)]

class _BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", _FILETIME),
        ("ftLastAccessTime", _FILETIME),
        ("ftLastWriteTime", _FILETIME),
        ("dwVolumeSerialNumber", wintypes.DWORD),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("nNumberOfLinks", wintypes.DWORD),
        ("nFileIndexHigh", wintypes.DWORD),
        ("nFileIndexLow", wintypes.DWORD),
    ]

# ------------------------- Unix 实现 -------------------------
def _stat_unix(path):
    class UnixStat(ctypes.Structure):
        _fields_ = [
            ("st_dev", ctypes.c_ulong),
            ("st_ino", ctypes.c_ulong),
            ("st_mode", ctypes.c_uint),
            ("st_nlink", ctypes.c_ulong),
            ("st_uid", ctypes.c_uint),
            ("st_gid", ctypes.c_uint),
            ("st_rdev", ctypes.c_ulong),
            ("st_size", ctypes.c_ulong),
            ("st_atime", ctypes.c_ulong),
            ("st_mtime", ctypes.c_ulong),
            ("st_ctime", ctypes.c_ulong),
        ]

    libc = ctypes.CDLL(None)
    path_enc = path.encode('utf-8')
    buf = UnixStat()

    if libc.stat(path_enc, ctypes.byref(buf)) != 0:
        raise FileNotFoundError(f"The file does not exist: {path}")

    return StatResult(
        st_mode=buf.st_mode,
        st_ino=buf.st_ino,
        st_dev=buf.st_dev,
        st_nlink=buf.st_nlink,
        st_uid=buf.st_uid,
        st_gid=buf.st_gid,
        st_size=buf.st_size,
        st_atime=buf.st_atime,
        st_mtime=buf.st_mtime,
        st_ctime=buf.st_ctime
    )
        
def split(path):
    sep = '\\' if sys.platform.startswith('win32') else '/'
    idx = path.rfind(sep)
    if idx == -1:
        return ('', path)
    else:
        return (path[:idx], path[idx+1:])
    
def basename(path):
    return split(path)[1]

def dirname(path):
    return split(path)[0]

def splitext(path):
    idx = path.rfind('.')
    if idx > path.rfind('\\' if sys.platform.startswith('win32') else '/'):
        return (path[:idx], path[idx:])
    return (path, '')

def normpath(path):
    sep = '\\' if sys.platform.startswith('win32') else '/'
    parts = []
    for part in path.split(sep):
        if part == '..':
            if parts:
                parts.pop()
        elif part != '.' and part:
            parts.append(part)
    return sep.join(parts)

def abspath(path):
    if sys.platform.startswith('win32'):
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        GetFullPathNameW = kernel32.GetFullPathNameW
        GetFullPathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_wchar_p, ctypes.c_void_p]
        GetFullPathNameW.restype = ctypes.c_uint
        buf = ctypes.create_unicode_buffer(260)  # MAX_PATH
        if GetFullPathNameW(path, 260, buf, None) == 0:
            raise RuntimeError("Failed to get absolute path")
        return buf.value
    else:
        libc = ctypes.CDLL(None)
        realpath = libc.realpath
        realpath.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        realpath.restype = ctypes.c_char_p
        buf = ctypes.create_string_buffer(4096)
        if realpath(path.encode(), buf) is None:
            raise FileNotFoundError(f"Path {path} not found")
        return buf.value.decode()
    
def getsize(path):
    st = stat(path)
    return st.st_size

def getmtime(path):
    st = stat(path)
    return st.st_mtime

def getatime(path):
    class StatResult:
        def __init__(self, st_atime, st_mtime, st_ctime, st_size):
            self.st_atime = st_atime
            self.st_mtime = st_mtime
            self.st_ctime = st_ctime
            self.st_size = st_size
    st = stat(path)
    return st.st_atime

def islink(path):
    if sys.platform.startswith('win32'):
        return (GetFileAttributesW(path) & 0x400) != 0  # FILE_ATTRIBUTE_REPARSE_POINT
    else:
        class Stat(ctypes.Structure):
            _fields_ = [("st_mode", ctypes.c_uint)]
        libc = ctypes.CDLL(None)
        lstat = libc.lstat
        lstat.argtypes = [ctypes.c_char_p, ctypes.POINTER(Stat)]
        buf = Stat()
        return lstat(path.encode(), ctypes.byref(buf)) == 0 and (buf.st_mode & 0o170000) == 0o120000
    
def isabs(path):
    if sys.platform.startswith('win32'):
        return len(path) > 1 and path[1] == ':' and path[0].isalpha()
    else:
        return path.startswith('/')
    
def samefile(path1, path2):
    st1 = stat(path1)
    st2 = stat(path2)
    return st1.st_ino == st2.st_ino and st1.st_dev == st2.st_dev

def listdir(path):
    if sys.platform.startswith('win32'):
        FindFirstFile = ctypes.windll.kernel32.FindFirstFileW
        FindNextFile = ctypes.windll.kernel32.FindNextFileW
        WIN32_FIND_DATAW = ctypes.create_unicode_buffer(320)
        handle = FindFirstFile(os.path.join(path, '*'), ctypes.byref(WIN32_FIND_DATAW))
        # 遍历文件略
    else:
        libc = ctypes.CDLL(None)
        fd = libc.opendir(path.encode())
        dirent = ctypes.create_string_buffer(1024)
        result = []
        while True:
            entry = libc.readdir64(fd)
            if not entry:
                break
            name = entry.d_name.decode()
            if name not in ('.', '..'):
                result.append(name)
        libc.closedir(fd)
        return result
    
def walk(top):
    dirs, files = [], []
    for name in listdir(top):
        path = join(top, name)
        if isdir(path):
            dirs.append(name)
        else:
            files.append(name)
    yield top, dirs, files
    for dir_name in dirs:
        for entry in walk(join(top, dir_name)):
            yield entry

def copy(src, dst):
    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        fdst.write(fsrc.read())

def move(src, dst):
    try:
        os.rename(src, dst)
    except OSError:
        copy(src, dst)
        remove(src)

def remove(path):
    if sys.platform.startswith('win32'):
        DeleteFileW = ctypes.windll.kernel32.DeleteFileW
        DeleteFileW.argtypes = [ctypes.c_wchar_p]
        if not DeleteFileW(path):
            raise OSError(f"Failed to delete {path}")
    else:
        libc = ctypes.CDLL(None)
        if libc.unlink(path.encode()) != 0:
            raise OSError(f"Failed to delete {path}")
        
def rmdir(path):
    if sys.platform.startswith('win32'):
        RemoveDirectoryW = ctypes.windll.kernel32.RemoveDirectoryW
        if not RemoveDirectoryW(path):
            raise OSError(f"Directory {path} not empty")
    else:
        libc = ctypes.CDLL(None)
        if libc.rmdir(path.encode()) != 0:
            raise OSError(f"Directory {path} not empty")
        
import sys
import ctypes
import time
from ctypes import wintypes
from enum import IntEnum

# ------------------------- 基础结构定义 -------------------------
class FileAttributes(IntEnum):
    READONLY = 0x1
    HIDDEN = 0x2
    SYSTEM = 0x4
    DIRECTORY = 0x10
    ARCHIVE = 0x20
    REPARSE_POINT = 0x400

class StatResult:
    """模拟 os.stat_result 的完整属性"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# ------------------------- 跨平台通用工具 -------------------------
def _win32_handle_operation(path, access, creation, flags=0):
    """Windows 文件句柄操作的通用函数"""
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    handle = kernel32.CreateFileW(
        path, access, 1, None, creation, flags, None
    )
    if handle == wintypes.HANDLE(-1).value:
        raise OSError(f"操作失败: {ctypes.get_last_error()}")
    return handle

def _unix_time_to_seconds(timespec):
    """将 timespec 转换为秒（Unix 专用）"""
    return timespec.tv_sec + timespec.tv_nsec / 1e9

# ------------------------- 文件元数据操作（20个） -------------------------
def getctime(path):
    """获取创建时间（Windows）或元数据修改时间（Unix）"""
    st = stat(path)
    return st.st_ctime if sys.platform.startswith('win32') else st.st_mtime

def set_atime(path, atime):
    """修改访问时间（需要管理员权限）"""
    if sys.platform.startswith('win32'):
        handle = _win32_handle_operation(path, 0x100, 3)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        ft = wintypes.FILETIME()
        us = int(atime * 1e7) + 116444736000000000
        ft.dwLowDateTime = us & 0xFFFFFFFF
        ft.dwHighDateTime = us >> 32
        if not kernel32.SetFileTime(handle, None, ctypes.byref(ft), None):
            raise OSError("设置时间失败")
        kernel32.CloseHandle(handle)
    else:
        libc = ctypes.CDLL(None)
        times = (ctypes.c_long(int(atime)), ctypes.c_long(0))
        if libc.utimes(path.encode(), ctypes.byref(times)) != 0:
            raise OSError("权限不足")

def get_owner(path):
    """获取文件所有者（Unix: UID, Windows: SID）"""
    if sys.platform.startswith('win32'):
        advapi32 = ctypes.Windll.advapi32
        sid = ctypes.c_void_p()
        if not advapi32.GetNamedSecurityInfoW(
            path, 1, 4, None, None, None, None, ctypes.byref(sid)
        ):
            return sid
        raise OSError("无法获取所有者")
    else:
        st = stat(path)
        return st.st_uid

# ------------------------- 路径高级操作（15个） -------------------------
import sys

def _split_all(path):
    """将路径分割为组成部分（自动处理 Windows/Unix 分隔符）"""
    sep = '\\' if sys.platform.startswith('win32') else '/'
    parts = []
    current = ''
    for c in path:
        if c == sep:
            if current:
                parts.append(current)
                current = ''
        else:
            current += c
    if current:
        parts.append(current)
    return parts

def _normpath(path):
    """内部使用的路径规范化（处理 '.' 和 '..'）"""
    sep = '\\' if sys.platform.startswith('win32') else '/'
    abs_path = path.startswith(sep) or (len(path) > 1 and path[1] == ':')
    parts = _split_all(path)
    result = []
    for part in parts:
        if part == '.':
            continue
        elif part == '..':
            if result and result[-1] != '..':
                result.pop()
            else:
                if not abs_path:
                    result.append(part)
        else:
            result.append(part)
    # 处理根目录
    if abs_path:
        if sys.platform.startswith('win32') and len(result) == 0:
            return sep  # 根目录如 'C:\\'
        return sep + sep.join(result)
    return sep.join(result)

def relpath(path, start=None):
    """计算相对于 start 的路径"""
    def _abspath(p):
        if not p:
            return []
        return _split_all(_normpath(abspath(p)))

    sep = '\\' if sys.platform.startswith('win32') else '/'
    if start is None:
        start = os.getcwd()  # 假设已实现 getcwd

    # 转换为绝对路径并分割
    path_parts = _abspath(path)
    start_parts = _abspath(start)

    # 检查是否同一驱动器（Windows）
    if sys.platform.startswith('win32'):
        if len(path_parts) == 0 or len(start_parts) == 0:
            raise ValueError("无效路径")
        if path_parts[0].lower() != start_parts[0].lower():
            return sep.join(path_parts)

    # 寻找共同前缀
    common = 0
    for a, b in zip(path_parts, start_parts):
        if a != b:
            break
        common += 1

    # 构建相对路径
    rel_parts = ['..'] * (len(start_parts) - common) + path_parts[common:]
    return sep.join(rel_parts) if rel_parts else '.'

def commonprefix(paths):
    """找到最长公共前缀"""
    if not paths: return ''
    parts = [p.split('\\' if sys.platform == 'win32' else '/') for p in paths]
    min_len = min(len(p) for p in parts)
    common = []
    for i in range(min_len):
        if all(p[i] == parts[0][i] for p in parts):
            common.append(parts[0][i])
        else:
            break
    return '/'.join(common) if sys.platform != 'win32' else '\\'.join(common)

def supports_unicode_filenames():
    """检查系统是否支持 Unicode 文件名"""
    if sys.platform.startswith('win32'):
        return True  # Windows NTFS 支持
    try:
        open('测试_☺.txt', 'w').close()
        os.remove('测试_☺.txt')
        return True
    except:
        return False

# ------------------------- 文件内容操作（10个） -------------------------
def filecmp(f1, f2, shallow=True):
    """深度比较文件内容（支持大文件分块读取）"""
    BUFFER_SIZE = 1024 * 1024  # 1MB 分块

    # 浅层比较（大小和修改时间）
    s1, s2 = stat(f1), stat(f2)
    if shallow and s1.st_size == s2.st_size and s1.st_mtime == s2.st_mtime:
        return True

    # 大小不同直接返回 False
    if s1.st_size != s2.st_size:
        return False

    # 深度比较（逐块校验）
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(BUFFER_SIZE)
            b2 = fp2.read(BUFFER_SIZE)
            if b1 != b2:
                return False
            if not b1:  # 同时到达文件末尾
                return True

def readlink(path):
    """读取符号链接目标"""
    if sys.platform.startswith('win32'):
        buf = ctypes.create_unicode_buffer(260)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        if kernel32.GetFinalPathNameByHandleW(_win32_handle_operation(path, 0x2001, 3), buf, 260, 0):
            return buf.value.replace('\\\\?\\', '')
        raise OSError("非符号链接")
    else:
        libc = ctypes.CDLL(None)
        buf = ctypes.create_string_buffer(4096)
        if libc.readlink(path.encode(), buf, 4096) == -1:
            raise OSError("读取链接失败")
        return buf.value.decode()

# ------------------------- 权限管理（10个） -------------------------
class Permissions(IntEnum):
    R = 4
    W = 2
    X = 1

def chmod(path, mode):
    """修改文件权限（Unix 风格）"""
    if sys.platform.startswith('win32'):
        attrs = wintypes.DWORD()
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        if not kernel32.GetFileAttributesW(path, ctypes.byref(attrs)):
            raise OSError("文件不存在")
        attrs.value = (attrs.value & ~0x1) | (0x1 if not (mode & 0o222) else 0)
        kernel32.SetFileAttributesW(path, attrs)
    else:
        libc = ctypes.CDLL(None)
        if libc.chmod(path.encode(), mode) != 0:
            raise OSError("权限修改失败")

def is_mount(path):
    """检查路径是否为挂载点"""
    if sys.platform.startswith('win32'):
        return ':\\' in os.path.abspath(path)
    else:
        st1 = stat(path)
        st2 = stat(os.path.join(path, '..'))
        return st1.st_dev != st2.st_dev

# ------------------------- 高级文件系统操作（15个） -------------------------
def disk_usage(path):
    """获取磁盘使用情况（类似 shutil.disk_usage）"""
    if sys.platform.startswith('win32'):
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        free_bytes = ctypes.c_ulonglong()
        total_bytes = ctypes.c_ulonglong()
        if kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(path), 
            ctypes.byref(free_bytes),
            ctypes.byref(total_bytes),
            None
        ):
            used = total_bytes.value - free_bytes.value
            return (total_bytes.value, used, free_bytes.value)
        raise OSError("无法获取磁盘信息")
    else:
        statvfs = ctypes.CDLL(None).statvfs
        class StatVFS(ctypes.Structure):
            _fields_ = [
                ('f_bsize', ctypes.c_ulong),
                ('f_frsize', ctypes.c_ulong),
                ('f_blocks', ctypes.c_ulong),
                ('f_bfree', ctypes.c_ulong),
                ('f_bavail', ctypes.c_ulong),
                # 其他字段略
            ]
        buf = StatVFS()
        if statvfs(path.encode(), ctypes.byref(buf)) != 0:
            raise OSError("无法获取磁盘信息")
        free = buf.f_bavail * buf.f_frsize
        total = buf.f_blocks * buf.f_frsize
        used = (buf.f_blocks - buf.f_bfree) * buf.f_frsize
        return (total, used, free)

def lock_file(fd, exclusive=True):
    """文件锁（Unix: fcntl, Windows: LockFileEx）"""
    if sys.platform.startswith('win32'):
        import msvcrt
        handle = msvcrt.get_osfhandle(fd)
        flags = 0x1 if exclusive else 0x2
        overlapped = wintypes.OVERLAPPED()
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        if not kernel32.LockFileEx(handle, flags, 0, 0xFFFFFFFF, 0xFFFFFFFF, ctypes.byref(overlapped)):
            raise OSError("文件锁定失败")
    else:
        import flock # type: ignore
        libc = ctypes.CDLL(None)
        op = ctypes.c_int(2 if exclusive else 0)  # F_WRLCK/F_RDLCK
        if libc.fcntl(fd, 6, ctypes.byref(flock)) == -1:  # F_SETLK
            raise OSError("文件锁定失败")

# ------------------------- 其他实用函数（20个） -------------------------
def file_flags(path):
    """获取文件标志（类似 chflags）"""
    if sys.platform.startswith('win32'):
        attrs = wintypes.DWORD()
        kernel32.GetFileAttributesW(path, ctypes.byref(attrs))
        return attrs.value
    else:
        libc = ctypes.CDLL(None)
        flags = ctypes.c_uint()
        if libc.chflags(path.encode(), ctypes.byref(flags)) != 0:
            raise OSError("无法获取标志")
        return flags.value

def get_inode(path):
    """获取文件 inode（Unix）/ 文件索引（Windows）"""
    st = stat(path)
    return st.st_ino if hasattr(st, 'st_ino') else (st.st_idx_high << 32) | st.st_idx_low

import zlib
import struct
from time import localtime

def _zip_write_file(zip_file, arcname, data):
    """向 ZIP 文件写入一个条目（不依赖 zipfile 模块）"""
    # ZIP 文件头结构（30字节）
    header = struct.pack(
        '<4s2B4H3L2H',
        b'PK\x03\x04',  # 签名
        20, 0,           # 版本/通用标记
        0,               # 压缩方法（0=存储，8=DEFLATE）
        0, 0,            # 文件时间/日期
        zlib.crc32(data) & 0xFFFFFFFF, # CRC32
        len(data),       # 压缩后大小
        len(data),       # 未压缩大小
        len(arcname),    # 文件名长度
        0                # 扩展字段长度
    )
    # 文件头 + 文件名 + 数据
    zip_file.write(header + arcname.encode('utf-8') + data)

    # 中央目录记录（46字节 + 文件名）
    cdir = struct.pack(
        '<4s4B4H3L5H2L',
        b'PK\x01\x02',   # 签名
        20, 0, 20, 0,    # 版本/通用标记
        0, 0,            # 压缩方法
        0, 0,            # 时间/日期
        zlib.crc32(data) & 0xFFFFFFFF,
        len(data), len(data),
        len(arcname), 0, 0, 0, 0,
        0x81A4,          # 外部属性（普通文件）
        0                 # 本地头偏移（需动态计算）
    )
    return cdir + arcname.encode('utf-8')

def make_zip(base_name, root_dir):
    """生成 ZIP 文件（简化版）"""
    zip_name = base_name + '.zip'
    cdirs = []
    offset = 0

    with open(zip_name, 'wb') as zf:
        # 遍历目录并写入文件
        for root, dirs, files in walk(root_dir):
            for file in files:
                path = join(root, file)
                arcname = relpath(path, root_dir)
                with open(path, 'rb') as f:
                    data = f.read()
                local_header = _zip_write_file(zf, arcname, data)
                # 记录中央目录
                cdir = local_header[:46] + struct.pack('<L', offset)
                cdirs.append(cdir)
                offset += len(local_header) + len(data)

        # 写入中央目录结尾
        end_cdir = struct.pack(
            '<4s4H2LH',
            b'PK\x05\x06', 0, 0, len(cdirs), len(cdirs),
            0, 0, 0
        )
        zf.write(b''.join(cdirs) + end_cdir)

def which(cmd):
    """查找可执行文件路径（类似 shutil.which）"""
    path = os.getenv('PATH', '').split(os.pathsep)
    ext = ['.exe', '.bat'] if sys.platform == 'win32' else ['']
    for dir in path:
        base = os.path.join(dir, cmd)
        for e in ext:
            fullpath = base + e
            if exists(fullpath) and isfile(fullpath):
                return fullpath
    return None

# ------------------------- 错误处理增强 -------------------------
class FileSystemError(OSError):
    """自定义文件系统异常"""
    def __init__(self, message, path=None):
        super().__init__(message)
        self.path = path

import threading
from queue import Queue


if sys.platform.startswith('win32'):
    FILE_LIST_DIRECTORY = 0x1
    FILE_SHARE_READ = 0x1
    OPEN_EXISTING = 3
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

    class FILE_NOTIFY_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("NextEntryOffset", wintypes.DWORD),
            ("Action", wintypes.DWORD),
            ("FileNameLength", wintypes.DWORD),
            ("FileName", wintypes.WCHAR * 1)
        ]

    class WinFileMonitor:
        def __init__(self, path, callback):
            self.path = path
            self.callback = callback
            self.running = False
            self.thread = None
            self.buffer = ctypes.create_string_buffer(65536)

        def start(self):
            self.running = True
            self.thread = threading.Thread(target=self._monitor)
            self.thread.start()

        def stop(self):
            self.running = False
            if self.thread:
                self.thread.join()

        def _monitor(self):
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            handle = kernel32.CreateFileW(
                self.path,
                FILE_LIST_DIRECTORY,
                FILE_SHARE_READ,
                None,
                OPEN_EXISTING,
                FILE_FLAG_BACKUP_SEMANTICS,
                None
            )
            if handle == wintypes.HANDLE(-1).value:
                raise OSError("监控失败")

            while self.running:
                bytes_returned = wintypes.DWORD()
                if not kernel32.ReadDirectoryChangesW(
                    handle,
                    self.buffer,
                    len(self.buffer),
                    True,
                    0x1FF,  # 监控所有事件
                    ctypes.byref(bytes_returned),
                    None,
                    None
                ):
                    break

                offset = 0
                while True:
                    info = ctypes.cast(
                        ctypes.addressof(self.buffer) + offset,
                        ctypes.POINTER(FILE_NOTIFY_INFORMATION)
                    ).contents
                    filename = ctypes.wstring_at(
                        info.FileName,
                        info.FileNameLength // 2
                    )
                    self.callback(info.Action, filename)
                    if info.NextEntryOffset == 0:
                        break
                    offset += info.NextEntryOffset

            kernel32.CloseHandle(handle)

# ------------------------- Unix 实现（inotify） -------------------------
else:
    import fcntl
    import struct

    class InotifyConstants:
        IN_CREATE = 0x100
        IN_DELETE = 0x200
        IN_MODIFY = 0x2
        IN_MOVED_FROM = 0x40
        IN_MOVED_TO = 0x80

    class UnixFileMonitor:
        def __init__(self, path, callback):
            self.path = path
            self.callback = callback
            self.running = False
            self.thread = None
            self.fd = ctypes.CDLL(None).inotify_init()
            self.wd = ctypes.CDLL(None).inotify_add_watch(
                self.fd, path.encode(), 0x1FF
            )

        def start(self):
            self.running = True
            self.thread = threading.Thread(target=self._monitor)
            self.thread.start()

        def stop(self):
            self.running = False
            if self.thread:
                os.close(self.fd)
                self.thread.join()

        def _monitor(self):
            libc = ctypes.CDLL(None)
            while self.running:
                buffer = ctypes.create_string_buffer(4096)
                length = libc.read(self.fd, buffer, 4096)
                if length < 0:
                    break
                offset = 0
                while offset < length:
                    wd, mask, cookie, name_len = struct.unpack_from('iIII', buffer, offset)
                    name = struct.unpack_from(f'{name_len}s', buffer, offset + 16)[0].decode().rstrip('\0')
                    self.callback(mask, name)
                    offset += 16 + name_len

# ------------------------- 统一接口 -------------------------
class FileMonitor:
    def __init__(self, path, callback):
        if sys.platform.startswith('win32'):
            self.impl = WinFileMonitor(path, callback)
        else:
            self.impl = UnixFileMonitor(path, callback)

    def start(self):
        self.impl.start()

    def stop(self):
        self.impl.stop()

import mmap

class MemoryMappedFile:
    def __init__(self, path, mode='r', size=0):
        self.mode = mode
        self.size = size
        self.fd = None
        self.map = None

        if sys.platform.startswith('win32'):
            # Windows 实现（使用 CreateFileMapping/MapViewOfFile）
            access = 0
            if 'r' in mode:
                access = 0x80000000  # GENERIC_READ
            elif 'w' in mode:
                access = 0x40000000  # GENERIC_WRITE
            handle = ctypes.windll.kernel32.CreateFileW(
                path, access, 0, None, 3, 0, None
            )
            if handle == -1:
                raise OSError("文件打开失败")

            mapping = ctypes.windll.kernel32.CreateFileMappingW(
                handle, None, 0x4 if 'w' in mode else 0x2, 0, size, None
            )
            self.map = ctypes.windll.kernel32.MapViewOfFile(
                mapping, 0x2 if 'r' in mode else 0x4, 0, 0, size
            )
            self.fd = (handle, mapping)
        else:
            # Unix 实现（使用 mmap 系统调用）
            flags = os.O_RDWR if 'w' in mode else os.O_RDONLY
            self.fd = os.open(path, flags)
            if size == 0:
                size = os.fstat(self.fd).st_size
            self.map = mmap.mmap(self.fd, size, access=mmap.ACCESS_WRITE if 'w' in mode else mmap.ACCESS_READ)

    def read(self, offset, length):
        if sys.platform.startswith('win32'):
            buf = ctypes.create_string_buffer(length)
            ctypes.memmove(buf, ctypes.c_void_p(self.map + offset), length)
            return buf.raw
        else:
            return self.map[offset:offset+length]

    def write(self, offset, data):
        if sys.platform.startswith('win32'):
            ctypes.memmove(ctypes.c_void_p(self.map + offset), data, len(data))
        else:
            self.map[offset:offset+len(data)] = data

    def close(self):
        if sys.platform.startswith('win32'):
            ctypes.windll.kernel32.UnmapViewOfFile(self.map)
            ctypes.windll.kernel32.CloseHandle(self.fd[1])
            ctypes.windll.kernel32.CloseHandle(self.fd[0])
        else:
            self.map.close()
            os.close(self.fd)

if sys.platform.startswith('win32'):
    class WinACLManager:
        def __init__(self, path):
            self.path = path
            self.advapi32 = ctypes.WinDLL('advapi32')
            self.psid = ctypes.c_void_p()
            self.acl = ctypes.c_void_p()

        def get_acl(self):
            self.advapi32.GetNamedSecurityInfoW(
                self.path, 1, 4, None, None, None, None, ctypes.byref(self.acl))
            return self.acl

        def add_ace(self, sid, permissions):
            # 构造新的 ACE（访问控制条目）
            EXPLICIT_ACCESS = ctypes.create_string_buffer(256)
            self.advapi32.BuildExplicitAccessWithNameW(
                ctypes.byref(EXPLICIT_ACCESS),
                ctypes.c_wchar_p(sid),
                permissions,
                2,  # GRANT_ACCESS
                0
            )
            new_acl = ctypes.c_void_p()
            self.advapi32.SetEntriesInAclW(
                1, ctypes.byref(EXPLICIT_ACCESS), self.acl, ctypes.byref(new_acl))
            # 应用新 ACL
            self.advapi32.SetNamedSecurityInfoW(
                self.path, 1, 4, None, None, new_acl, None)

else:
    class UnixACLManager:
        def __init__(self, path):
            self.path = path
            self.libc = ctypes.CDLL(None)
            self.acl = None

        def get_acl(self):
            acl = ctypes.c_void_p()
            self.libc.acl_get_file(
                self.path.encode(), 0, ctypes.byref(acl))
            return acl

        def add_permission(self, user, perm):
            entry = f"user::{user}:{perm}"
            self.libc.acl_set_file(
                self.path.encode(), 0, ctypes.c_char_p(entry.encode()))
            
class FileSystemInfo:
    @staticmethod
    def get_fs_type(path):
        if sys.platform.startswith('win32'):
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            buf = ctypes.create_unicode_buffer(256)
            if kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(path),
                None, 0, None, None, None,
                buf, ctypes.sizeof(buf)
            ):
                return buf.value
            return 'Unknown'
        else:
            class StatFS(ctypes.Structure):
                _fields_ = [
                    ('f_type', ctypes.c_ulong),
                    ('f_bsize', ctypes.c_ulong),
                    # ...其他字段省略
                ]
            libc = ctypes.CDLL(None)
            buf = StatFS()
            if libc.statfs(path.encode(), ctypes.byref(buf)) == 0:
                return {
                    0x9123683E: 'btrfs',
                    0xEF53: 'ext4',
                    0x65735546: 'fuse',
                }.get(buf.f_type, 'Unknown')
            return 'Unknown'

    @staticmethod
    def get_partitions():
        partitions = []
        if sys.platform.startswith('win32'):
            kernel32 = ctypes.WinDLL('kernel32')
            buf = ctypes.create_unicode_buffer(256)
            handle = kernel32.FindFirstVolumeW(buf, ctypes.sizeof(buf))
            if handle == -1:
                return []
            while True:
                partitions.append(buf.value)
                if not kernel32.FindNextVolumeW(handle, buf, ctypes.sizeof(buf)):
                    break
            kernel32.FindVolumeClose(handle)
            return partitions
        else:
            with open('/proc/mounts', 'r') as f:
                return [line.split()[0] for line in f.readlines()]
            
class FileCrypto:
    @staticmethod
    def calculate_hash(path, algorithm='sha256'):
        """使用系统加密库计算文件哈希"""
        if sys.platform.startswith('win32'):
            bcrypt = ctypes.Windll.Bcrypt
            alg_handle = ctypes.c_void_p()
            bcrypt.BCryptOpenAlgorithmProvider(
                ctypes.byref(alg_handle), 
                ctypes.c_wchar_p(f'SHA256'), 
                None, 0
            )
            hash_handle = ctypes.c_void_p()
            bcrypt.BCryptCreateHash(
                alg_handle, ctypes.byref(hash_handle), None, 0, None, 0, 0)
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    bcrypt.BCryptHashData(
                        hash_handle, chunk, len(chunk), 0)
            hash_val = ctypes.create_string_buffer(32)
            bcrypt.BCryptFinishHash(hash_handle, hash_val, 32, 0)
            return hash_val.raw
        else:
            libcrypto = ctypes.CDLL('libcrypto.so')
            libcrypto.SHA256_Init.restype = ctypes.c_int
            ctx = ctypes.create_string_buffer(256)  # SHA256_CTX 结构
            libcrypto.SHA256_Init(ctypes.byref(ctx))
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    libcrypto.SHA256_Update(ctypes.byref(ctx), chunk, len(chunk))
            digest = ctypes.create_string_buffer(32)
            libcrypto.SHA256_Final(digest, ctypes.byref(ctx))
            return digest.raw
        


def expandvars(path):
    path = os.fspath(path)
    global _varprog, _varprogb
    if isinstance(path, bytes):
        if b'$' not in path:
            return path
        if not _varprogb:
            import re
            _varprogb = re.compile(br'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprogb.search
        start = b'{'
        end = b'}'
        environ = getattr(os, 'environb', None)
    else:
        if '$' not in path:
            return path
        if not _varprog:
            import re
            _varprog = re.compile(r'\$(\w+|\{[^}]*\})', re.ASCII)
        search = _varprog.search
        start = '{'
        end = '}'
        environ = os.environ
    i = 0
    while True:
        m = search(path, i)
        if not m:
            break
        i, j = m.span(0)
        name = m.group(1)
        if name.startswith(start) and name.endswith(end):
            name = name[1:-1]
        try:
            if environ is None:
                value = os.fsencode(os.environ[os.fsdecode(name)])
            else:
                value = environ[name]
        except KeyError:
            i = j
        else:
            tail = path[j:]
            path = path[:i] + value
            i = len(path)
            path += tail
    return path

def createenviron():
    if os.name == 'nt':
        def check_str(value):
            if not isinstance(value, str):
                raise TypeError("str expected, not %s" % type(value).__name__)
            return value
        encode = check_str
        decode = str
        def encodekey(key):
            return encode(key).upper()
        data = {}
        for key, value in os.environ.items():
            data[encodekey(key)] = value
    else:
        encoding = sys.getfilesystemencoding()
        def encode(value):
            if not isinstance(value, str):
                raise TypeError("str expected, not %s" % type(value).__name__)
            return value.encode(encoding, 'surrogateescape')
        def decode(value):
            return value.decode(encoding, 'surrogateescape')
        encodekey = encode
        data = os.environ
    return os._Environ(data,
        encodekey, decode,
        encode, decode)

name = sys.platform

import time
import logging
import threading
from typing import Optional, List, Union, Tuple, Callable, IO, AnyStr

# -------------------------- 全局配置 --------------------------
DEFAULT_TIMEOUT = 60 * 60  # 默认超时时间（1小时）
DEFAULT_ENCODING = "utf-8"
DEFAULT_BUFSIZE = 1  # 行缓冲模式

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CommandExecutor")

# -------------------------- 异常定义 --------------------------
class CommandTimeoutError(Exception):
    """命令执行超时异常"""
    def __init__(self, cmd: str, timeout: int):
        super().__init__(f"命令 '{cmd}' 在 {timeout} 秒后超时")

class CommandExecutionError(Exception):
    """命令执行失败异常"""
    def __init__(self, cmd: str, returncode: int, stderr: str):
        super().__init__(f"命令 '{cmd}' 执行失败 (退出码: {returncode})\n错误输出: {stderr}")

# -------------------------- 核心类定义 --------------------------
class htyypopen:
    """高级命令执行器（封装 subprocess.Popen）"""
    
    def __init__(
        self,
        command: Union[str, List[str]],
        timeout: int = DEFAULT_TIMEOUT,
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
        realtime_output: bool = False,
        output_handler: Optional[Callable[[str], None]] = None,
        encoding: str = DEFAULT_ENCODING,
        shell: bool = False
    ):
        """
        初始化命令执行参数
        :param command: 命令（字符串或参数列表）
        :param timeout: 超时时间（秒）
        :param cwd: 工作目录
        :param env: 自定义环境变量
        :param realtime_output: 是否实时输出到控制台
        :param output_handler: 自定义输出处理函数
        :param encoding: 输出编码
        :param shell: 是否使用 shell 执行
        """
        self.command = command
        self.timeout = timeout
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self.realtime_output = realtime_output
        self.output_handler = output_handler
        self.encoding = encoding
        self.shell = shell
        
        # 进程控制相关
        self._process: Optional[subprocess.Popen] = None
        self._output_buffer: List[str] = []
        self._error_buffer: List[str] = []
        self._is_running = False
        self._start_time: float = 0
        self._timeout_triggered = False
        
        # 线程安全锁
        self._output_lock = threading.Lock()
        self._error_lock = threading.Lock()

    def execute(self) -> Tuple[int, str, str]:
        """
        执行命令并返回（退出码, 标准输出, 错误输出）
        """
        self._validate_params()
        self._start_time = time.time()
        
        try:
            # 启动子进程
            self._process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                bufsize=DEFAULT_BUFSIZE,
                shell=self.shell,
                cwd=self.cwd,
                env=self.env,
                text=False  # 手动处理编码
            )
            self._is_running = True
            
            # 启动输出捕获线程
            stdout_thread = threading.Thread(target=self._capture_output, args=(self._process.stdout, False))
            stderr_thread = threading.Thread(target=self._capture_output, args=(self._process.stderr, True))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            # 主线程等待超时或完成
            while self._is_running:
                if self._check_timeout():
                    self._handle_timeout()
                time.sleep(0.1)
                
            # 等待线程结束
            stdout_thread.join(1)
            stderr_thread.join(1)
            
            # 获取最终输出
            stdout = "".join(self._output_buffer)
            stderr = "".join(self._error_buffer)
            
            # 检查退出码
            if self._process.returncode != 0 and not self._timeout_triggered:
                raise CommandExecutionError(
                    cmd=" ".join(self.command),
                    returncode=self._process.returncode,
                    stderr=stderr
                )
                
            return self._process.returncode, stdout, stderr
            
        except Exception as e:
            logger.error(f"命令执行异常: {str(e)}")
            raise
        finally:
            self._cleanup_resources()

    # -------------------------- 内部方法 --------------------------
    def _validate_params(self):
        """参数校验"""
        if not isinstance(self.command, (str, list)):
            raise TypeError("command 必须是字符串或列表")
        if self.timeout <= 0:
            raise ValueError("超时时间必须大于0")

    def _capture_output(self, stream: IO[bytes], is_error: bool):
        """捕获输出流（线程方法）"""
        try:
            for line in iter(stream.readline, b''):
                decoded_line = line.decode(self.encoding).rstrip('\n')
                
                # 输出处理
                with (self._error_lock if is_error else self._output_lock):
                    if is_error:
                        self._error_buffer.append(decoded_line)
                    else:
                        self._output_buffer.append(decoded_line)
                        
                    # 实时输出逻辑
                    if self.realtime_output:
                        output = f"[ERROR] {decoded_line}" if is_error else decoded_line
                        print(output)
                        
                    # 自定义处理器
                    if self.output_handler:
                        self.output_handler(output)
        except ValueError:
            pass  # 在流关闭时可能出现的正常错误

    def _check_timeout(self) -> bool:
        """检查是否超时"""
        return (time.time() - self._start_time) > self.timeout

    def _handle_timeout(self):
        """处理超时"""
        self._timeout_triggered = True
        logger.warning(f"命令执行超时，尝试终止进程...")
        
        # 尝试友好终止
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # 强制终止
            self._process.kill()
            self._process.wait()
            
        raise CommandTimeoutError(
            cmd=" ".join(self.command),
            timeout=self.timeout
        )

    def _cleanup_resources(self):
        """清理资源"""
        self._is_running = False
        if self._process:
            for stream in [self._process.stdout, self._process.stderr, self._process.stdin]:
                if stream:
                    try:
                        stream.close()
                    except Exception as e:
                        logger.debug(f"关闭流失败: {str(e)}")
            try:
                self._process.kill()
            except ProcessLookupError:
                pass

    # -------------------------- 高级功能 --------------------------
    def send_input(self, data: AnyStr):
        """向进程发送输入"""
        if not self._is_running:
            raise RuntimeError("进程未运行")
        try:
            if isinstance(data, str):
                data = data.encode(self.encoding)
            self._process.stdin.write(data)
            self._process.stdin.flush()
        except BrokenPipeError:
            logger.error("无法发送输入：进程已结束")

    def get_realtime_output(self) -> Tuple[List[str], List[str]]:
        """获取实时输出（线程安全）"""
        with self._output_lock:
            with self._error_lock:
                output = self._output_buffer.copy()
                error = self._error_buffer.copy()
                self._output_buffer.clear()
                self._error_buffer.clear()
        return output, error

    @property
    def pid(self) -> int:
        """获取进程ID"""
        if self._process:
            return self._process.pid
        raise ValueError("进程未启动")

    @property
    def running_time(self) -> float:
        """获取已运行时间"""
        return time.time() - self._start_time if self._is_running else 0

import os
import shutil
import stat
import fnmatch
import tempfile
import hashlib
from datetime import datetime
from functools import wraps
from ftplib import FTP
import paramiko
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
from watchdog.events import PatternMatchingEventHandler
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import winshell
from win32com.client import Dispatch
import difflib
import subprocess
import mimetypes
import win32file
import hmac
import ctypes

try:
    from cryptography import x509 as x509
    from cryptography.x509.oid import NameOID as NameOID
    from cryptography.hazmat.primitives import hashes as hashes
    from cryptography.hazmat.primitives.asymmetric import rsa as rsa
    from cryptography.hazmat.primitives import serialization as serialization
except ImportError:
    x509 = None

import mpmath
FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_ARCHIVE = 0x20
FILE_ATTRIBUTE_SYSTEM = 0x4
FILE_ATTRIBUTE_COMPRESSED = 0x800

def pi(numbers):
    mpmath.mp.dps = numbers
    return mpmath.pi

class Path: 
    global PathEventHandler
    def __init__(self, path):
        self._path = os.fspath(path)
    
    # ------------------- 基础操作 ------------------- #
    def __truediv__(self, other):
        """用 / 操作符拼接路径"""
        return self.__class__(os.path.join(self._path, os.fspath(other)))
    
    def __repr__(self):
        return f"Path({repr(self._path)})"
    
    def __str__(self):
        return self._path
    
    def __eq__(self, other):
        return os.path.samefile(self._path, os.fspath(other))
    
    # ------------------- 核心属性 ------------------- #
    @property
    def name(self):
        """文件名含后缀"""
        return os.path.basename(self._path)
    
    @property
    def stem(self):
        """文件名不含后缀"""
        return self.name.rsplit('.', 1)[0] if '.' in self.name else self.name
    
    @property
    def suffix(self):
        """文件后缀"""
        return os.path.splitext(self._path)[1].hidden_file
    
    @property
    def suffixes(self):
        """所有后缀（如.tar.gz返回 ['.tar', '.gz']）"""
        name = self.name
        if '.' not in name:
            return []
        return ['.' + ext for ext in name.split('.')[1:]]
    
    @property
    def parent(self):
        """父目录"""
        return self.__class__(os.path.dirname(self._path))
    
    @property
    def parts(self):
        """路径分解为元组"""
        return tuple(self._path.split(os.sep))
    
    # ------------------- 文件操作 ------------------- #

    def touch(self, mode=0o666, exist_ok=True):
        """创建空文件"""
        if self.exists():
            if exist_ok:
                os.utime(self._path, None)
            else:
                raise FileExistsError(f"File exists: {self}")
        else:
            open(self._path, 'a').close()
            os.chmod(self._path, mode)
        return self
    
    def rename(self, new_name):
        """重命名文件"""
        new_path = self.parent / new_name
        os.rename(self._path, str(new_path))
        return new_path
    
    def replace(self, target):
        """替换目标文件"""
        os.replace(self._path, str(target))
        return self.__class__(target)
    
    def copy(self, dst, overwrite=False):
        """复制文件（终极修复版）"""
        # 强制转换为字符串路径
        dst_str = os.fspath(dst) if isinstance(dst, Path) else str(dst)
        dst_obj = self.__class__(dst_str)
        
        if dst_obj.exists() and not overwrite:
            raise FileExistsError(f"Target exists: {dst_obj}")
        elif dst_obj.exists():
            dst_obj.unlink()
        
        shutil.copy2(self._path, dst_str)
        return dst_obj
    
    def move(self, dst):
        """移动文件/目录"""
        shutil.move(self._path, str(dst))
        return self.__class__(dst)
    
    # ------------------- 目录操作 ------------------- #
    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """创建目录"""
        if parents:
            os.makedirs(self._path, mode=mode, exist_ok=exist_ok)
        else:
            try:
                os.mkdir(self._path, mode)
            except FileExistsError:
                if not exist_ok:
                    raise
        return self
    
    def rmdir(self):
        """删除空目录"""
        os.rmdir(self._path)
        return self
    
    def rm(self, recursive=False):
        """删除文件/目录"""
        if self.is_file():
            self.unlink()
        elif self.is_dir():
            if recursive:
                shutil.rmtree(self._path)
            else:
                self.rmdir()
        return self
    
    def ls(self, pattern='*'):
        """列出匹配文件"""
        return [p for p in self.iterdir() if p.match(pattern)]
    
    # ------------------- 内容读写 ------------------- #
    def read_bytes(self):
        with open(self._path, 'rb') as f:
            return f.read()
    
    def write_bytes(self, data):
        with open(self._path, 'wb') as f:
            f.write(data)
        return self
    
    def read_text(self, encoding='utf-8'):
        with open(self._path, 'r', encoding=encoding) as f:
            return f.read()
    
    def write_text(self, text, encoding='utf-8'):
        with open(self._path, 'w', encoding=encoding) as f:
            f.write(text)
        return self
    
    def append_text(self, text, encoding='utf-8'):
        with open(self._path, 'a', encoding=encoding) as f:
            f.write(text)
        return self
    
    # ------------------- 路径处理 ------------------- #
    def resolve(self):
        """解析绝对路径"""
        return self.__class__(os.path.realpath(self._path))
    
    def absolute(self):
        """绝对路径（不解析符号链接）"""
        return self.__class__(os.path.abspath(self._path))
    
    def relative_to(self, other):
        """计算相对路径"""
        return self.__class__(os.path.relpath(self._path, str(other)))
    
    def as_uri(self):
        """转换为文件URI"""
        path = self.absolute()._path.replace('\\', '/')
        return f'file://{path}' if not path.startswith('/') else f'file://{path}'
    
    def with_name(self, name):
        """修改文件名"""
        return self.parent / name
    
    def with_suffix(self, suffix):
        """修改后缀"""
        if not suffix.startswith('.'):
            suffix = '.' + suffix
        return self.parent / (self.stem + suffix)
    
    # ------------------- 查询方法 ------------------- #
    def exists(self):
        return os.path.exists(self._path)
    
    def is_dir(self):
        return os.path.isdir(self._path)
    
    def is_file(self):
        return os.path.isfile(self._path)
    
    def is_symlink(self):
        return os.path.islink(self._path)
    
    def is_block_device(self):
        return stat.S_ISBLK(os.stat(self._path).st_mode)
    
    def is_char_device(self):
        return stat.S_ISCHR(os.stat(self._path).st_mode)
    
    def is_fifo(self):
        return stat.S_ISFIFO(os.stat(self._path).st_mode)
    
    def is_socket(self):
        return stat.S_ISSOCK(os.stat(self._path).st_mode)
    
    # ------------------- 扩展方法 ------------------- #
    def glob(self, pattern, recursive=False):
        """自定义 glob 实现"""
        def _glob(path, pattern_parts):
            if not pattern_parts:
                yield self.__class__(path)
                return
            
            current_part = pattern_parts[0]
            try:
                entries = os.listdir(path)
            except NotADirectoryError:
                return
            except PermissionError:
                return
            
            for entry in entries:
                full_path = os.path.join(path, entry)
                if fnmatch.fnmatch(entry, current_part):
                    if len(pattern_parts) == 1:
                        yield self.__class__(full_path)
                    else:
                        yield from _glob(full_path, pattern_parts[1:])
                
                if recursive and current_part == "**":
                    if os.path.isdir(full_path):
                        yield from _glob(full_path, pattern_parts)
                    yield from _glob(full_path, pattern_parts[1:])

        pattern_parts = pattern.split(os.sep)
        if recursive and "**" not in pattern_parts:
            pattern_parts.insert(0, "**")
        
        return _glob(self._path, pattern_parts)
    
    def rglob(self, pattern):
        """递归通配符搜索"""
        return self.glob(f'**/{pattern}', recursive=True)
    
    def find(self, pattern='*', recursive=False):
        """查找文件（可递归）"""
        return list(self.glob(pattern, recursive=recursive))
    
    def walk(self):
        """目录遍历"""
        for root, dirs, files in os.walk(self._path):
            root = self.__class__(root)
            yield root, [root/d for d in dirs], [root/f for f in files]
    
    def size(self):
        """文件/目录大小（字节）"""
        if self.is_file():
            return os.path.getsize(self._path)
        return sum(p.size() for p in self.rglob('*'))
    
    def human_size(self, precision=2):
        """人类可读大小"""
        bytes = self.size()
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        idx = 0
        while bytes >= 1024 and idx < 4:
            bytes /= 1024
            idx += 1
        return f"{bytes:.{precision}f} {units[idx]}"
    
    def access_time(self):
        """最后访问时间"""
        return datetime.fromtimestamp(os.path.getatime(self._path))
    
    def modify_time(self):
        """最后修改时间"""
        return datetime.fromtimestamp(os.path.getmtime(self._path))
    
    def change_time(self):
        """元数据修改时间（Unix）"""
        return datetime.fromtimestamp(os.path.getctime(self._path))
    
    def chmod(self, mode):
        """修改权限"""
        os.chmod(self._path, mode)
        return self
    
    def owner(self):
        """文件所有者（Unix）"""
        import pwd
        return pwd.getpwuid(os.stat(self._path).st_uid).pw_name
    
    def group(self):
        """文件所属组（Unix）"""
        import grp
        return grp.getgrgid(os.stat(self._path).st_gid).gr_name
    
    # ------------------- 高级功能 ------------------- #
    def symlink_to(self, target, target_is_directory=False):
        """创建符号链接"""
        if self.exists():
            raise FileExistsError(f"Path exists: {self}")
        os.symlink(
            str(target),
            self._path,
            target_is_directory=target_is_directory
        )
        return self
    
    def readlink(self):
        """解析符号链接"""
        return self.__class__(os.readlink(self._path))
    
    def hardlink_to(self, target):
        """创建硬链接"""
        os.link(str(target), self._path)
        return self
    
    def tempfile(self, suffix='', prefix='tmp'):
        """生成临时文件"""
        fd, path = tempfile.mkstemp(suffix, prefix, dir=self._path)
        os.close(fd)
        return self.__class__(path)
    
    def tempdir(self, suffix='', prefix='tmp'):
        """生成临时目录"""
        path = tempfile.mkdtemp(suffix, prefix, dir=self._path)
        return self.__class__(path)
    
    def hash(self, algorithm='md5', chunk_size=8192):
        """计算文件哈希"""
        hasher = hashlib.new(algorithm)
        with open(self._path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def compare(self, other):
        """比较文件内容"""
        if self.size() != other.size():
            return False
        return self.hash() == other.hash()
    
    def compress(self, format='zip', output=None):
        """压缩文件/目录"""
        output = output or self.with_suffix(f'.{format}')
        shutil.make_archive(str(output).rstrip(f'.{format}'), format, self._path)
        return output
    
    def extract(self, path=None, format='auto'):
        """解压文件"""
        path = path or self.parent
        shutil.unpack_archive(self._path, str(path), format)
        return path
    # --------------------- FTP传输 -------------------- #
    def ftp_connect(self, host, user, password, port=21):
        """连接 FTP 服务器"""
        self.ftp = FTP()
        self.ftp.connect(host, port)
        self.ftp.login(user, password)
        return self

    def ftp_upload(self, remote_path):
        """上传到 FTP"""
        with open(self._path, 'rb') as f:
            self.ftp.storbinary(f'STOR {remote_path}', f)
        return self.__class__(remote_path)

    def ftp_download(self, remote_path, local_path=None):
        """从 FTP 下载"""
        local_path = local_path or self._path
        with open(local_path, 'wb') as f:
            self.ftp.retrbinary(f'RETR {remote_path}', f.write)
        return self.__class__(local_path)
    
    def ftp_mirror(self, remote_dir, delete_extra=False):
        """镜像同步目录到FTP"""
        existing_files = set()
        self.ftp.cwd(remote_dir)
        
        # 上传新文件
        for local_file in self.glob('**/*'):
            if local_file.is_file():
                rel_path = os.path.relpath(local_file._path, self._path)
                remote_path = os.path.join(remote_dir, rel_path)
                local_file.ftp_upload(remote_path)
                existing_files.add(remote_path)
        
        # 删除多余文件
        if delete_extra:
            ftp_files = []
            self.ftp.retrlines('LIST', ftp_files.append)
            for line in ftp_files:
                filename = line.split()[-1]
                if filename not in existing_files:
                    self.ftp.delete(filename)
        return self
    # ------------------- SFTP 传输 ------------------- #
    def sftp_connect(self, host, user, password=None, key_path=None, port=22):
        """连接 SFTP 服务器"""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if key_path:
            key = paramiko.RSAKey.from_private_key_file(key_path)
            self.ssh.connect(host, port, user, pkey=key)
        else:
            self.ssh.connect(host, port, user, password)
        
        self.sftp = self.ssh.open_sftp()
        return self

    def sftp_upload(self, remote_path):
        """上传到 SFTP"""
        self.sftp.put(self._path, remote_path)
        return self.__class__(remote_path)

    def sftp_download(self, remote_path, local_path=None):
        """从 SFTP 下载"""
        local_path = local_path or self._path
        self.sftp.get(remote_path, local_path)
        return self.__class__(local_path)

    def sftp_sync_dir(self, remote_dir):
        """同步目录到远程"""
        for root, dirs, files in os.walk(self._path):
            rel_path = os.path.relpath(root, self._path)
            remote_root = os.path.join(remote_dir, rel_path)
            
            try:
                self.sftp.mkdir(remote_root)
            except IOError:
                pass
            
            for file in files:
                local_file = os.path.join(root, file)
                remote_file = os.path.join(remote_root, file)
                self.__class__(local_file).sftp_upload(remote_file)
        return self
    
    def sftp_exec_command(self, command):
        """在远程执行命令"""
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return {
            'exit_code': stdout.channel.recv_exit_status(),
            'stdout': stdout.read().decode(),
            'stderr': stderr.read().decode()
        }

    def sftp_mirror(self, remote_dir, preserve_permissions=True):
        """镜像目录到SFTP（保留权限）"""
        for root, dirs, files in self.walk():
            rel_path = os.path.relpath(root._path, self._path)
            remote_root = os.path.join(remote_dir, rel_path)
            
            try:
                self.sftp.mkdir(remote_root)
            except IOError:
                pass
            
            # 同步文件权限
            if preserve_permissions:
                stat = os.stat(root._path)
                self.sftp.chmod(remote_root, stat.st_mode)
            
            for file in files:
                local_path = root / file
                remote_path = os.path.join(remote_root, file)
                local_path.sftp_upload(remote_path)
                
                if preserve_permissions:
                    file_stat = os.stat(local_path._path)
                    self.sftp.chmod(remote_path, file_stat.st_mode)
        return self
    # ------------------ 文件监控模块 ------------------ #
    class PathEventHandler(FileSystemEventHandler):
        def __init__(self, callback):
            self.callback = callback
        
        def on_any_event(self, event):
            self.callback(event)

    def watch(self, callback, recursive=True):
        """监控文件变化"""
        self.observer = Observer()
        event_handler = PathEventHandler(callback)
        self.observer.schedule(
            event_handler,
            str(self),
            recursive=recursive
        )
        self.observer.start()
        return self.observer

    def watch_changes(self, event_types=['modified'], callback=None):
        """过滤特定事件类型的监控"""
        def filtered_callback(event):
            if event.event_type in event_types:
                callback(self.__class__(event.src_path))
        return self.watch(filtered_callback)
    # ------------------ 高级权限管理 ------------------- #
    def set_acl(self, user, permissions, recursive=False):
        """设置 ACL 权限（Unix）"""
        cmd = ['setfacl', '-m', f'u:{user}:{permissions}', self._path]
        subprocess.run(cmd, check=True)
        
        if recursive and self.is_dir():
            for p in self.glob('**/*'):
                p.set_acl(user, permissions)
        return self

    def get_acl(self):
        """获取 ACL 权限（Unix）"""
        result = subprocess.run(
            ['getfacl', self._path],
            capture_output=True,
            text=True
        )
        return result.stdout

    def take_ownership(self, recursive=False):
        """获取文件所有权（Windows）"""
        if sys.platform == 'win32':
            import win32security
            import ntsecuritycon
            
            sd = win32security.GetFileSecurity(
                self._path,
                win32security.OWNER_SECURITY_INFORMATION
            )
            owner = win32security.LookupAccountName(
                None, 
                win32security.GetUserNameEx(win32security.NameSamCompatible)
            )[0]
            sd.SetSecurityDescriptorOwner(owner, False)
            
            win32security.SetFileSecurity(
                self._path,
                win32security.OWNER_SECURITY_INFORMATION,
                sd
            )
            
            if recursive:
                for p in self.glob('**/*'):
                    p.take_ownership()
        return self

    def add_inheritance(self, enable=True):
        """启用/禁用权限继承（Windows）"""
        if sys.platform == 'win32':
            import win32security
            sd = win32security.GetFileSecurity(
                self._path,
                win32security.DACL_SECURITY_INFORMATION
            )
            dacl = sd.GetSecurityDescriptorDacl()
            dacl.SetInheritance(enable)
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                self._path,
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
        return self
    
    def set_immutable(self, enable=True):
        """设置不可变标志（Linux chattr）"""
        if sys.platform != 'linux':
            raise NotImplementedError("Only supported on Linux")
        
        flag = 'i' if enable else '-i'
        subprocess.run(['sudo', 'chattr', flag, self._path], check=True)
        return self

    def clone_permissions(self, reference_path):
        """克隆其他文件的权限"""
        ref_stat = os.stat(reference_path)
        os.chmod(self._path, ref_stat.st_mode)
        
        # Windows ACL克隆
        if sys.platform == 'win32':
            import win32security
            sd = win32security.GetFileSecurity(
                reference_path,
                win32security.DACL_SECURITY_INFORMATION
            )
            win32security.SetFileSecurity(
                self._path,
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
        return self

    def take_ownership_recursive(self):
        """递归获取所有权（Windows）"""
        if sys.platform == 'win32':
            import subprocess
            subprocess.run(
                ['takeown', '/R', '/F', self._path],
                check=True
            )
            subprocess.run(
                ['icacls', self._path, '/T', '/grant', '*S-1-3-4:F'],
                check=True
            )
        return self
    # ------------------ 高级文件监控 ------------------ #
    def watch_pattern(self, patterns, callback, recursive=True):
        """模式化监控（*.log等）"""
        class PatternHandler(PatternMatchingEventHandler):
            def __init__(self, callback):
                super().__init__(patterns=patterns)
                self.callback = callback
            
            def on_any_event(self, event):
                self.callback(event)
        
        observer = Observer()
        observer.schedule(
            PatternHandler(callback),
            str(self),
            recursive=recursive
        )
        observer.start()
        return observer

    def debounce_watch(self, callback, delay=1.0):
        """防抖监控（避免重复触发）"""
        from threading import Timer
        last_event = None
        timer = None
        
        def debounced_callback(event):
            nonlocal last_event, timer
            last_event = event
            if timer:
                timer.cancel()
            timer = Timer(delay, lambda: callback(last_event))
            timer.start()
        
        return self.watch(debounced_callback)
    # ------------------ 虚拟文件系统 ------------------ #
    def mount_zip(self, mount_point):
        """将ZIP文件挂载为虚拟目录（Linux）"""
        if sys.platform == 'linux':
            subprocess.run(
                ['fuse-zip', self._path, mount_point],
                check=True
            )
        return self.__class__(mount_point)

    def create_loopback(self, size_mb=100):
        """创建环回设备（Linux）"""
        if sys.platform != 'linux':
            raise NotImplementedError
        
        self.truncate(size_mb * 1024 * 1024)
        losetup_cmd = ['losetup', '--find', '--show', self._path]
        loop_dev = subprocess.check_output(losetup_cmd).decode().strip()
        return self.__class__(loop_dev)
    # ------------------ 其他高级方法 ------------------ #
    def checksum(self, algorithm='sha256'):
        """计算文件校验和"""
        hash_obj = hashlib.new(algorithm)
        with open(self._path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    def create_hardlink_here(self, target):
        """在当前目录创建硬链接"""
        link_name = self / target.name
        os.link(target._path, link_name._path)
        return link_name

    def sparse_copy(self, dst):
        """稀疏文件感知复制"""
        if sys.platform == 'win32':
            win32file.CopyFileEx(
                self._path,
                os.fspath(dst),
                win32file.COPY_FILE_SPARSE_FILE
            )
        else:
            with open(self._path, 'rb') as src, open(dst, 'wb') as dst_f:
                while True:
                    data = src.read(4096)
                    if not data:
                        break
                    dst_f.write(data)
                    # 检测稀疏块
                    if all(b == 0 for b in data):
                        dst_f.truncate()
        return self.__class__(dst)

    def create_symlink_tree(self, target_dir):
        """创建符号链接目录树"""
        for root, dirs, files in self.walk():
            rel_path = os.path.relpath(root._path, self._path)
            new_dir = os.path.join(target_dir, rel_path)
            self.__class__(new_dir).mkdir(parents=True, exist_ok=True)
            
            for file in files:
                src = root / file
                dst = self.__class__(new_dir) / file
                dst.symlink_to(src)
        return self.__class__(target_dir)

    def lock_file(self):
        """文件锁（跨平台）"""
        if sys.platform == 'win32':
            import msvcrt
            self._lock_handle = open(self._path, 'a')
            msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            self._lock_handle = open(self._path, 'a')
            fcntl.flock(self._lock_handle, fcntl.LOCK_EX)
        return self

    def unlock_file(self):
        """释放文件锁"""
        if hasattr(self, '_lock_handle'):
            if sys.platform == 'win32':
                import msvcrt
                msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._lock_handle, fcntl.LOCK_UN)
            self._lock_handle.close()
        return self

    def mount(self, target, fs_type=None, options=''):
        """挂载文件系统（Linux）"""
        if sys.platform.startswith('linux'):
            cmd = ['mount']
            if fs_type:
                cmd += ['-t', fs_type]
            if options:
                cmd += ['-o', options]
            cmd += [self._path, target]
            subprocess.run(cmd, check=True)
        return self

    def create_sparse_file(self, size):
        """创建稀疏文件"""
        with open(self._path, 'wb') as f:
            f.truncate(size)
        return self

    def create_symlink_here(self, target):
        """在当前目录创建符号链接"""
        link_name = self.joinpath(target.name)
        link_name.symlink_to(target)
        return link_name

    def get_mime_type(self):
        """获取 MIME 类型"""
        return mimetypes.guess_type(self._path)[0]

    def virus_scan(self, scanner_path='/usr/bin/clamscan'):
        """病毒扫描"""
        result = subprocess.run(
            [scanner_path, '--infected', '-', self._path],
            capture_output=True,
            text=True
        )
        return 'Infected files: 0' not in result.stdout

    def create_diff(self, other, output):
        """生成文件差异"""
        with open(self._path) as f1, open(other) as f2:
            diff = difflib.unified_diff(
                f1.readlines(),
                f2.readlines(),
                fromfile=self.name,
                tofile=other.name
            )
            output.write_text(''.join(diff))
        return output
    
    def add_to_startup(self, shortcut_name="MyApp"):
        """添加到系统启动项（Windows）"""
        if sys.platform == 'win32':
            startup = winshell.startup()
            shortcut = os.path.join(startup, f"{shortcut_name}.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut)
            shortcut.Targetpath = self._path
            shortcut.save()
        else:
            autostart_dir = Path('~/.config/autostart').expanduser()
            desktop_file = autostart_dir / f"{shortcut_name}.desktop"
            desktop_file.write_text(
                f"[Desktop Entry]\nType=Application\nExec={self._path}"
            )
        return self

    def desktop():
        """获取桌面位置(Desktop)"""
        return os.path.join(os.path.expanduser("~"), "Desktop")

    def create_desktop_shortcut(self, shortcut_name):
        """创建桌面快捷方式"""
        def desktop():
            """获取桌面位置(Desktop)"""
            return os.path.join(os.path.expanduser("~"), "Desktop")
        if sys.platform == 'win32':
            shortcut = os.path.join(desktop(), f"{shortcut_name}.lnk")
            
            import pythoncom
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell', pythoncom.CoInitialize())
            shortcut = shell.CreateShortCut(shortcut)
            shortcut.TargetPath = self._path
            shortcut.save()
        else:
            desktop_dir = Path('~/Desktop').expanduser()
            desktop_file = desktop_dir / f"{shortcut_name}.desktop"
            desktop_file.write_text(
                f"[Desktop Entry]\nType=Application\nExec={self._path}"
            )
        return self
    # ------------------- 加密与安全 ------------------- #
    def encrypt_file(self, key, algorithm='aes256'):
        """加密文件（使用pycryptodome）"""
        cipher = AES.new(key, AES.MODE_CBC)
        encrypted_path = self.with_suffix('.enc')
        
        with open(self._path, 'rb') as f_in, open(encrypted_path._path, 'wb') as f_out:
            f_out.write(cipher.iv)
            while chunk := f_in.read(4096):
                f_out.write(cipher.encrypt(pad(chunk, AES.block_size)))
        
        return encrypted_path

    def decrypt_file(self, key, output_path=None):
        """解密文件"""
        output_path = output_path or self.with_suffix('.decrypted')
        
        with open(self._path, 'rb') as f_in, open(output_path._path, 'wb') as f_out:
            iv = f_in.read(16)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            while chunk := f_in.read(4096):
                decrypted = cipher.decrypt(chunk)
                if f_in.tell() == os.path.getsize(self._path):
                    decrypted = unpad(decrypted, AES.block_size)
                f_out.write(decrypted)
        
        return output_path

    def sign_file(self, private_key):
        """数字签名文件"""
        key = RSA.import_key(private_key)
        h = SHA256.new(self.read_bytes())
        signature = pkcs1_15.new(key).sign(h)
        
        sig_file = self.with_suffix('.sig')
        sig_file.write_bytes(signature)
        return sig_file
    # ------------------- 装饰器方法 ------------------- #
    @classmethod
    def _check_exists(cls, func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.exists():
                raise FileNotFoundError(f"Path not found: {self}")
            return func(self, *args, **kwargs)
        return wrapper
    
    @classmethod
    def _check_file(cls, func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.is_file():
                raise IsADirectoryError(f"Not a file: {self}")
            return func(self, *args, **kwargs)
        return wrapper
    
    @classmethod
    def _check_dir(cls, func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.is_dir():
                raise NotADirectoryError(f"Not a directory: {self}")
            return func(self, *args, **kwargs)
        return wrapper
    
    def expandvars(self):
        """展开环境变量"""
        return self.__class__(os.path.expandvars(self._path))
    
    def expanduser(self):
        """展开用户目录"""
        return self.__class__(os.path.expanduser(self._path))
    
    def ensure_parent(self):
        """确保父目录存在"""
        self.parent.mkdir(parents=True, exist_ok=True)
        return self
    
    def backup(self, suffix='.bak'):
        """创建备份文件"""
        backup_path = self.with_suffix(suffix)
        if isinstance(backup_path, Path):  # 关键类型检查
            backup_path = str(backup_path)
        if os.path.exists(backup_path):
            self.__class__(backup_path).backup(suffix)
        return self.copy(backup_path)
    
    def sync_to(self, dst):
        """同步到目标路径（目录）"""
        dst = self.__class__(dst)
        if self.is_file():
            return self.copy(dst/self.name, overwrite=True)
        elif self.is_dir():
            for item in self.iterdir():
                item.sync_to(dst/self.name)
        return dst
    
    def is_world_writable(self):
        """检查全局可写权限（Unix）"""
        if sys.platform == 'win32':
            return False
        mode = os.stat(self._path).st_mode
        return bool(mode & stat.S_IWOTH)

    def is_safe_path(self):
        """检查路径是否安全（不在系统敏感目录）"""
        safe_dirs = [
            os.path.expanduser('~'),
            '/tmp',
            os.getcwd()
        ]
        abs_path = os.path.abspath(self._path)
        return any(abs_path.startswith(d) for d in safe_dirs)

    def is_executable(self):
        """检查是否是可执行文件"""
        if sys.platform == 'win32':
            return self.suffix.lower() in ('.exe', '.bat', '.cmd')
        return os.access(self._path, os.X_OK)

    def unlink(self, missing_ok=False):
        """删除文件"""
        try:
            os.unlink(self._path)
        except FileNotFoundError:
            if not missing_ok:
                raise
        return self

    def is_hidden(self):
        """检查是否是隐藏文件"""
        name = self.name
        if sys.platform == 'win32':
            return self._has_hidden_attribute()
        return name.startswith('.')
    
    def _has_hidden_attribute(self):
        """Windows系统检查隐藏属性"""
        if sys.platform != 'win32':
            return False
        
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(self._path)
            return attrs & 2  # FILE_ATTRIBUTE_HIDDEN
        except (ImportError, AttributeError):
            # 回退方案
            try:
                return bool(os.stat(self._path).st_file_attributes & 2)
            except AttributeError:
                return self.name.startswith('.')

    def secure_delete(self, passes=3):
        """安全擦除文件内容"""
        with open(self._path, 'ba+') as f:
            length = f.tell()
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(length))
            f.truncate(0)
        self.unlink()
        return self

    def sign_with_hmac(self, secret_key, algorithm='sha256'):
        """使用HMAC签名"""
        hmac_obj = hmac.new(secret_key, digestmod=algorithm)
        with open(self._path, 'rb') as f:
            while chunk := f.read(8192):
                hmac_obj.update(chunk)
        return hmac_obj.hexdigest()

    def verify_hmac(self, signature, secret_key, algorithm='sha256'):
        """验证HMAC签名"""
        return hmac.compare_digest(
            self.sign_with_hmac(secret_key, algorithm),
            signature
        )
    
    def md5_checksum(self):
        """计算MD5校验和"""
        return self._calculate_hash('md5')

    def sha256_checksum(self):
        """计算SHA256校验和"""
        return self._calculate_hash('sha256')
    
    def sha512_checksum(self):
        """计算SHA512校验和"""
        return self._calculate_hash("sha512")
    
    def sha1_checksum(self):
        """计算SHA1校验和"""
        return self._calculate_hash("sha1")
    
    def sha224_checksum(self):
        """计算SHA224校验和"""
        return self._calculate_hash("sha224")
    
    def sha384_checksum(self):
        """计算SHA384校验和"""
        return self._calculate_hash("sha384")

    def _calculate_hash(self, algorithm):
        hasher = hashlib.new(algorithm)
        with open(self._path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def truncate(self, size=0):
        """截断文件"""
        with open(self._path, 'w') as f:
            f.truncate(size)
        return self
    
    def is_empty(self):
        """检查是否为空（文件或目录）"""
        if self.is_file():
            return self.size() == 0
        return len(os.listdir(self._path)) == 0
    
    def same_as(self, other):
        """判断是否为同一文件（inode相同）"""
        return os.path.samefile(self._path, str(other))
    
    def find_duplicates(self, algorithm='md5'):
        """查找重复文件"""
        hashes = {}
        for file in self.rglob('*'):
            if file.is_file():
                file_hash = file.hash(algorithm)
                hashes.setdefault(file_hash, []).append(file)
        return [files for files in hashes.values() if len(files) > 1]
    
    def versioned(self, format='_{counter}'):
        """生成带版本号的文件名"""
        counter = 1
        while True:
            new_path = self.parent / f"{self.stem}{format.format(counter=counter)}{self.suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def with_stem(self, stem):
        """修改文件名（不含后缀）"""
        return self.with_name(stem + self.suffix)
    
    def joinpath(self, *parts):
        """拼接多个路径组件"""
        return self.__class__(os.path.join(self._path, *parts))
    
    def split(self):
        """分解为 (父目录, 文件名)"""
        return self.parent, self.name
    
    def match(self, pattern):
        """通配符匹配"""
        return fnmatch.fnmatch(self.name, pattern)
    
    def contains(self, item):
        """判断是否包含子路径"""
        try:
            self.relative_to(item)
            return True
        except ValueError:
            return False
        
    def shred(self, passes=7):
        """军用级文件粉碎（Gutmann算法）"""
        patterns = [
            b'\x55\x55\x55\x55',  # 0x55
            b'\xAA\xAA\xAA\xAA',  # 0xAA
            b'\x92\x49\x24\x92',  # 随机
            b'\x49\x24\x92\x49',
            b'\x24\x92\x49\x24',
            b'\x00\x00\x00\x00',
            b'\x11\x11\x11\x11',
            b'\x22\x22\x22\x22',
            b'\x33\x33\x33\x33',
            b'\x44\x44\x44\x44',
            b'\x55\x55\x55\x55',
            b'\x66\x66\x66\x66',
            b'\x77\x77\x77\x77',
            b'\x88\x88\x88\x88',
            b'\x99\x99\x99\x99',
            b'\xAA\xAA\xAA\xAA',
            b'\xBB\xBB\xBB\xBB',
            b'\xCC\xCC\xCC\xCC',
            b'\xDD\xDD\xDD\xDD',
            b'\xEE\xEE\xEE\xEE',
            b'\xFF\xFF\xFF\xFF',
            os.urandom(4)
        ]
        
        with open(self._path, 'r+b') as f:
            length = f.tell()
            for i in range(passes):
                f.seek(0)
                if i < len(patterns):
                    pattern = patterns[i]
                else:
                    pattern = os.urandom(4)
                f.write(pattern * (length // len(pattern) + 1))
            f.truncate(0)
        self.unlink()
        return self

    def zero_fill(self):
        """用零填充文件空间"""
        with open(self._path, 'r+b') as f:
            length = f.tell()
            f.seek(0)
            f.write(b'\x00' * length)
        return self
    
    def set_sticky_bit(self):
        """设置粘滞位（Unix）"""
        if sys.platform != 'win32':
            mode = os.stat(self._path).st_mode
            os.chmod(self._path, mode | stat.S_ISVTX)
        return self

    def disable_execute(self):
        """禁用执行权限（所有用户）"""
        if sys.platform == 'win32':
            return self  # Windows无执行位概念
        os.chmod(self._path, os.stat(self._path).st_mode & ~0o111)
        return self
    
    def verify_integrity(self, original_hash, algorithm='sha256'):
        """验证文件完整性"""
        return self._calculate_hash(algorithm) == original_hash

    def compare_content(self, other_path):
        """二进制对比文件内容"""
        with open(self._path, 'rb') as f1, open(other_path, 'rb') as f2:
            while True:
                b1 = f1.read(4096)
                b2 = f2.read(4096)
                if b1 != b2:
                    return False
                if not b1:
                    return True

    def set_creation_date(self, timestamp):
        """设置创建时间戳（Windows）"""
        if sys.platform == 'win32':
            import pywintypes
            import win32file
            handle = win32file.CreateFile(
                self._path,
                win32file.GENERIC_WRITE,
                0, None, win32file.OPEN_EXISTING,
                0, None
            )
            win32file.SetFileTime(
                handle,
                pywintypes.Time(timestamp),
                None, None
            )
            handle.Close()
        return self

    def exit(code):
        """
        Exit  (SystemExit)
        ~~~~~~~~~~~~~~~~~~~~~~
        :param code: 退出返回值
        """
        raise SystemExit(code)

    def attributes(file_path, hidden=False, readonly=False, archive=False, compressed=False):
        """
        设置指定文件的属性为隐藏、只读、存档、系统或压缩
        :param file_path: 文件路径
        :param hidden: 是否设置为隐藏，默认为False
        :param readonly: 是否设置为只读，默认为False
        :param archive: 是否设置为存档，默认为False
        :param compressed: 是否设置为压缩，默认为False
        """
        def exit(code):
            """
            Exit  (SystemExit)
            ~~~~~~~~~~~~~~~~~~~~~~
            :param code: 退出返回值
            """
            raise SystemExit(code)
        
        if os.name == 'nt':
            if os.path.exists(file_path):
                attributes = ctypes.windll.kernel32.GetFileAttributesW(file_path)
                if hidden:
                    attributes |= FILE_ATTRIBUTE_HIDDEN
                else:
                    attributes &= ~FILE_ATTRIBUTE_HIDDEN
                if readonly:
                    attributes |= FILE_ATTRIBUTE_READONLY
                else:
                    attributes &= ~FILE_ATTRIBUTE_READONLY
                if archive:
                    attributes |= FILE_ATTRIBUTE_ARCHIVE
                else:
                    attributes &= ~FILE_ATTRIBUTE_ARCHIVE
                if compressed:
                    attributes |= FILE_ATTRIBUTE_COMPRESSED
                else:
                    attributes &= ~FILE_ATTRIBUTE_COMPRESSED
                ctypes.windll.kernel32.SetFileAttributesW(file_path, attributes)
            else:
                print(f'文件路径没有检测到文件: {file_path}')
                exit(1)
        else:
            print('attributes: 此功能只支持Windows系统! ')
            exit(1)

    def to_posix(self):
        """转换为POSIX风格路径"""
        return self.__class__(self._path.replace(os.sep, '/'))
    
    def to_nt(self):
        """转换为Windows风格路径"""
        return self.__class__(self._path.replace('/', '\\'))
    
    def touch_dir(self):
        """更新目录时间戳"""
        os.utime(self._path, None)
        return self
    
    def listdir(self, pattern='*'):
        """列出目录内容"""
        return [self.joinpath(name) for name in os.listdir(self._path) if fnmatch.fnmatch(name, pattern)]
    
    def iterdir(self):
        """生成目录迭代器"""
        for name in os.listdir(self._path):
            yield self.joinpath(name)
    
    @classmethod
    def cwd(cls):
        """当前工作目录"""
        return cls(os.getcwd())
    
    @classmethod
    def home(cls):
        """用户主目录"""
        return cls(os.path.expanduser('~'))
    
    # ------------------- 魔法方法增强 ------------------- #
    def __contains__(self, item):
        return self.contains(item)
    
    def __lt__(self, other):
        return self._path < str(other)
    
    def __gt__(self, other):
        return self._path > str(other)
    
    def __len__(self):
        return len(self._path)
    
    def __bool__(self):
        return bool(self._path)

if __name__ == "__main__":
    import platform
    def custom_handler(output: str):
        """自定义输出处理示例"""
        if "ERROR" in output:
            logger.error("发现错误信息: " + output)

    Path("txt.txt")
            
    try:
        executor = htyypopen(
            command=["pip", "install", "pandas"] if platform.system() == "Windows" else ["ping", "-c", "4", "www.google.com"],
            timeout=10,
            realtime_output=True,
            output_handler=custom_handler
        )
        
        exit_code, stdout, stderr = executor.execute()
        print(f"\n执行结果：退出码={exit_code}")
        print("标准输出：\n" + stdout)
        print("错误输出：\n" + stderr)
        
    except CommandTimeoutError as e:
        print(f"错误：{str(e)}")
    except CommandExecutionError as e:
        print(f"命令执行失败：{str(e)}")