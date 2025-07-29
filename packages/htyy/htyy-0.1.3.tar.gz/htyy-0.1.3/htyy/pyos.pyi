"""
Python interface for the pyos C extension module
Version: 1.0
"""

import sys
from typing import Tuple, List, Optional, Any

# File operations
def mkdir(path: str, mode: int = 0o777) -> None:
    """
    Create a directory with specified mode
    
    Args:
        path: Directory path to create
        mode: Access mode (ignored on Windows)
    
    Raises:
        OSError: If directory creation fails
    """

if sys.platform == "win32":
    _PathLike = str | bytes  
else:
    _PathLike = str | bytes

def chdir(path: _PathLike) -> None: ...
def getcwd() -> str: ...
def makedirs(path: _PathLike, exist_ok: bool = ...) -> None: ...

def listdir(path: str) -> List[str]:
    """
    List directory contents
    
    Args:
        path: Directory path to list
    
    Returns:
        List of entry names in the directory
    
    Raises:
        OSError: If directory access fails
    """

def fsync(fd: int) -> None:
    """
    Synchronize file state to storage
    
    Args:
        fd: File descriptor to synchronize
    
    Raises:
        OSError: If synchronization fails
    """

def umask(mask: int) -> int:
    """
    Set file creation mask
    
    Args:
        mask: New umask value
    
    Returns:
        Previous umask value
    """

# Process management
def getpid() -> int:
    """
    Get current process ID
    
    Returns:
        Process ID as integer
    """

def system(command: str) -> int:
    """
    Execute shell command
    
    Args:
        command: Command string to execute
    
    Returns:
        Exit status of the command
    """

# System information
def cpu_count() -> int:
    """
    Get number of CPU cores
    
    Returns:
        Number of available processors
    
    Raises:
        OSError: If detection fails
    """

def sysconf(name: int) -> int:
    """
    Get system configuration value
    
    Args:
        name: Configuration parameter name
    
    Returns:
        Configuration value
    
    Raises:
        ValueError: For unsupported parameters
        OSError: If parameter retrieval fails
    """

def pathconf(path: str, name: int) -> int:
    """
    Get path configuration value
    
    Args:
        path: File system path
        name: Configuration parameter name
    
    Returns:
        Configuration value
    
    Raises:
        OSError: If parameter retrieval fails
    """

def getloadavg() -> Tuple[float, float, float]:
    """
    Get system load averages
    
    Returns:
        Tuple of 1, 5, and 15-minute load averages
    """

def terminal_size() -> Tuple[int, int]:
    """
    Get terminal dimensions
    
    Returns:
        Tuple of (columns, rows)
    """

# User/privilege management
def getuid() -> int:
    """
    Get current user ID
    
    Returns:
        User ID as integer
    """

def getlogin() -> str:
    """
    Get current login name
    
    Returns:
        Login name as string
    
    Raises:
        OSError: If name retrieval fails
    """

# Time/random functions
def clock_gettime(clk_id: int) -> Tuple[float, float]:
    """
    Get precise clock time
    
    Args:
        clk_id: Clock identifier
    
    Returns:
        Tuple of (seconds, nanoseconds)
    """

def urandom(size: int) -> bytes:
    """
    Generate cryptographically secure random bytes
    
    Args:
        size: Number of bytes to generate
    
    Returns:
        Bytes object with random data
    
    Raises:
        ValueError: For invalid size
        OSError: If random generation fails
    """

# Memory management
def mlock(buffer: bytes) -> None:
    """
    Lock memory pages
    
    Args:
        buffer: Memory buffer to lock
    
    Raises:
        OSError: If locking fails
    """

def munlock(buffer: bytes) -> None:
    """
    Unlock memory pages
    
    Args:
        buffer: Memory buffer to unlock
    """

# Error handling
def strerror(errnum: int) -> str:
    """
    Get error message string
    
    Args:
        errnum: Error number
    
    Returns:
        Error description string
    """

# Platform-specific implementations
if sys.platform != "win32":
    # POSIX-only functions
    def fork() -> int:
        """
        Create child process (POSIX only)
        
        Returns:
            0 in child, child PID in parent
        """

    def execv(path: str, args: List[str]) -> None:
        """
        Execute new program (POSIX only)
        
        Args:
            path: Path to executable
            args: Argument list
        """

    def setsid() -> int:
        """
        Create new session (POSIX only)
        
        Returns:
            Session ID
        """

    def kill(pid: int, sig: int) -> None:
        """
        Send signal to process (POSIX only)
        
        Args:
            pid: Target process ID
            sig: Signal number
        """

    def getpriority(which: int, who: int) -> int:
        """
        Get process priority (POSIX only)
        
        Returns:
            Nice value (-20 to 19)
        """

    def setpriority(which: int, who: int, priority: int) -> None:
        """
        Set process priority (POSIX only)
        
        Args:
            priority: Nice value (-20 to 19)
        """

else:
    # Windows-only functions
    def get_osfhandle(fd: int) -> int:
        """
        Get Windows file handle (Windows only)
        
        Args:
            fd: File descriptor
            
        Returns:
            Windows HANDLE value
        """

    def set_inheritable(fd: int, inheritable: bool) -> None:
        """
        Set handle inheritance flag (Windows only)
        
        Args:
            fd: File descriptor
            inheritable: True to enable inheritance
        """

# System constants
SC_PAGESIZE: int  # System page size constant
CLOCK_REALTIME: int  # System real-time clock
CLOCK_MONOTONIC: int  # Monotonic system clock

__all__ = [
    'mkdir', 'listdir', 'fsync', 'umask',
    'getpid', 'system', 'cpu_count', 'sysconf',
    'pathconf', 'getloadavg', 'terminal_size',
    'getuid', 'getlogin', 'clock_gettime',
    'urandom', 'mlock', 'munlock', 'strerror',
    'SC_PAGESIZE', 'CLOCK_REALTIME', 'CLOCK_MONOTONIC'
]

if sys.platform != "win32":
    __all__ += [
        'fork', 'execv', 'setsid', 'kill',
        'getpriority', 'setpriority'
    ]
else:
    __all__ += [
        'get_osfhandle', 'set_inheritable'
    ] 