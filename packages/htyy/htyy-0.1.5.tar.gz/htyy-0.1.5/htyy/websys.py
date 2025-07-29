import os
import sys
import platform
import subprocess
import socket
import requests
from typing import List, Optional

# ======================
# 系统控制函数
# ======================

def shutdown(delay: int = 0) -> bool:
    """关闭计算机
    :param delay: 延迟时间（秒）
    :return: 是否成功执行命令
    """
    try:
        if platform.system() == "Windows":
            subprocess.run(f"shutdown /s /t {delay}", shell=True, check=True)
        else:
            subprocess.run(f"shutdown -h +{delay//60}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def restart(delay: int = 0) -> bool:
    """重启计算机
    :param delay: 延迟时间（秒）
    """
    try:
        if platform.system() == "Windows":
            subprocess.run(f"shutdown /r /t {delay}", shell=True, check=True)
        else:
            subprocess.run(f"shutdown -r +{delay//60}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def lock_screen() -> bool:
    """锁定屏幕"""
    try:
        if platform.system() == "Windows":
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", check=True)
        elif platform.system() == "Darwin":
            subprocess.run("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend", 
                         shell=True, check=True)
        else:
            subprocess.run("dm-tool lock", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def system_sleep() -> bool:
    """进入睡眠模式"""
    try:
        if platform.system() == "Windows":
            subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", 
                          shell=True, check=True)
        elif platform.system() == "Darwin":
            subprocess.run("pmset sleepnow", shell=True, check=True)
        else:
            subprocess.run("systemctl suspend", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def logout_user() -> bool:
    """注销当前用户"""
    try:
        if platform.system() == "Windows":
            subprocess.run("shutdown /l", shell=True, check=True)
        elif platform.system() == "Darwin":
            subprocess.run("osascript -e 'tell app \"System Events\" to log out'", 
                          shell=True, check=True)
        else:
            subprocess.run("gnome-session-quit --no-prompt", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# ======================
# 网络工具函数
# ======================

def get_public_ip(timeout: int = 5) -> Optional[str]:
    """获取公共 IP 地址
    :param timeout: 请求超时时间（秒）
    :return: IP 地址字符串或 None
    """
    services = [
        "https://api.ipify.org",
        "https://ident.me",
        "https://ipinfo.io/ip"
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=timeout)
            return response.text.strip()
        except:
            continue
    return None

def resolve_domain(domain: str) -> List[str]:
    """解析域名 IP 地址
    :param domain: 要解析的域名（支持带协议头）
    :return: IP 地址列表
    """
    try:
        # 清理域名输入
        clean_domain = domain.lower().replace("https://", "").replace("http://", "")
        clean_domain = clean_domain.split("/")[0].split("?")[0]
        
        # 获取所有解析结果
        _, _, ipaddrlist = socket.gethostbyname_ex(clean_domain)
        return list(set(ipaddrlist))  # 去重
    except socket.gaierror:
        return []
    except Exception as e:
        print(f"解析错误: {str(e)}")
        return []

# ======================
# 辅助函数
# ======================

def require_admin() -> bool:
    """检查/请求管理员权限（Windows专用）"""
    if platform.system() == "Windows":
        try:
            # 检查是否是管理员
            from ctypes import windll
            if windll.shell32.IsUserAnAdmin():
                return True
            
            # 重新以管理员权限启动
            subprocess.run([
                "powershell",
                "-Command",
                f"Start-Process python -ArgumentList '{sys.argv[0]}' -Verb RunAs"
            ])
            sys.exit(0)
        except:
            return False
    return platform.system()

# ======================
# 使用示例
# ======================
if __name__ == "__main__":
    # 示例调用
    print("当前公网IP:", get_public_ip())
    print("GitHub的IP:", resolve_domain("https://github.com"))
    logout_user()
    """
    if require_admin():
        shutdown(60)  # 60秒后关机
    else:
        print("需要管理员权限执行此操作")"
    """