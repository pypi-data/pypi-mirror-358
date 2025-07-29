"""System"""

import subprocess
import os, sys, ctypes
import psutil, shutil, hashlib
from typing import Optional, Tuple, Dict, List

def IncreaseStart(Title, path):
    """
    Auto-start at boot.
    :param Title: The name of the auto-start service.
    :param path: File path.
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    subprocess.run(
        f'reg add HKCU\{key_path} /v "{Title}" /t REG_SZ /d "{path}" /f',
        shell=True
    )

def DeleteStart(Title):
    """
    Delete the startup auto-start item.
    :param Title: The auto-start service name to be removed.
    """
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    subprocess.run(
        f'reg delete HKCU\{key_path} /v "{Title}" /f',
        shell=True
    )


def CMD(command):
    """
    Execute shell command
    
    Args:
        command: Command string to execute
    
    Returns:
        Exit status of the command
    """
    from htyy import system
    system(command)

# ======================
# File System Operations
# ======================

def copy_file(src: str, dst: str) -> None:
    """Copy file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
    """
    shutil.copy(src, dst)

def delete_file(file_path: str) -> None:
    """Permanently delete a file.
    
    Args:
        file_path: Path to target file
    """
    if os.path.exists(file_path):
        os.remove(file_path)

def calculate_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Calculate file hash using specified algorithm.
    
    Args:
        file_path: Path to target file
        algorithm: Hash algorithm (md5/sha1/sha256)
        
    Returns:
        Hexadecimal digest string
    """
    hasher = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# ====================
# System Information
# ====================

def get_cpu_usage() -> float:
    """Get current CPU usage percentage.
    
    Returns:
        CPU usage as float (0.0-100.0)
    """
    return psutil.cpu_percent(interval=1)

def get_memory_status() -> Tuple[float, float]:
    """Get memory usage statistics.
    
    Returns:
        Tuple of (used_memory, total_memory) in GB
    """
    mem = psutil.virtual_memory()
    return (mem.used/1e9, mem.total/1e9)

def get_disk_usage(path: str = "/") -> Tuple[float, float]:
    """Get disk usage statistics for specified path.
    
    Args:
        path: Target path to check
        
    Returns:
        Tuple of (used_space, total_space) in GB
    """
    usage = psutil.disk_usage(path)
    return (usage.used/1e9, usage.total/1e9)

# ====================
# Process Management
# ====================

def start_process(executable_path: str) -> int:
    """Start a new process.
    
    Args:
        executable_path: Path to executable
        
    Returns:
        Process PID
    """
    proc = subprocess.Popen(executable_path)
    return proc.pid

def kill_process(pid: int) -> None:
    """Terminate a process by PID.
    
    Args:
        pid: Process ID to terminate
    """
    process = psutil.Process(pid)
    process.terminate()

# ====================
# Network Utilities
# ====================

def ping_host(host: str, count: int = 4) -> bool:
    """Check network connectivity to a host.
    
    Args:
        host: IP address or domain name
        count: Number of ping attempts
        
    Returns:
        True if host is reachable
    """
    result = subprocess.run(f"ping -n {count} {host}", 
                          stdout=subprocess.DEVNULL,
                          shell=True)
    return result.returncode == 0

def get_ip_address() -> Dict[str, List[str]]:
    """Get network interface IP addresses.
    
    Returns:
        Dictionary of {interface_name: [ip_addresses]}
    """
    addrs = psutil.net_if_addrs()
    return {k: [a.address for a in v if a.family == 2] 
            for k, v in addrs.items()}

# ====================
# Registry Operations
# ====================

def add_registry_key(key_path: str, value_name: str, 
                   value_data: str, hive: str = "HKCU") -> None:
    """Add/update registry key value.
    
    Args:
        key_path: Registry key path
        value_name: Value name
        value_data: Value data
        hive: Registry hive (HKCU/HKLM)
    """
    subprocess.run(f'reg add "{hive}\\{key_path}" /v "{value_name}" '
                  f'/t REG_SZ /d "{value_data}" /f', shell=True)

def delete_registry_key(key_path: str, value_name: str, 
                      hive: str = "HKCU") -> None:
    """Delete registry key value.
    
    Args:
        key_path: Registry key path
        value_name: Value name to delete
        hive: Registry hive (HKCU/HKLM)
    """
    subprocess.run(f'reg delete "{hive}\\{key_path}" /v "{value_name}" /f',
                  shell=True)

def query_registry_key(key_path: str, value_name: str, 
                     hive: str = "HKCU") -> Optional[str]:
    """Query registry key value.
    
    Args:
        key_path: Registry key path
        value_name: Value name to query
        hive: Registry hive (HKCU/HKLM)
        
    Returns:
        Value data or None if not found
    """
    result = subprocess.run(f'reg query "{hive}\\{key_path}" /v "{value_name}"',
                          capture_output=True, shell=True)
    if result.returncode != 0:
        return None
    return result.stdout.decode().split()[-1]

# ====================
# System Control
# ====================

def shutdown_system(timeout: int = 30) -> None:
    """Initiate system shutdown.
    
    Args:
        timeout: Shutdown timeout in seconds
    """
    subprocess.run(f"shutdown /s /t {timeout}", shell=True)

def restart_system(timeout: int = 30) -> None:
    """Initiate system restart.
    
    Args:
        timeout: Restart timeout in seconds
    """
    subprocess.run(f"shutdown /r /t {timeout}", shell=True)

def logoff_user() -> None:
    """Log off current user session."""
    ctypes.windll.user32.ExitWindowsEx(0, 0)

def lock_workstation() -> None:
    """Lock the workstation."""
    ctypes.windll.user32.LockWorkStation()

# ====================
# Clipboard Utilities
# ====================

def copy_to_clipboard(text: str) -> None:
    """Copy text to system clipboard.
    
    Args:
        text: Text to copy
    """
    subprocess.run("clip", input=text.strip().encode("utf-8"), shell=True)

def get_clipboard_text() -> str:
    """Retrieve text from system clipboard.
    
    Returns:
        Clipboard text content
    """
    result = subprocess.run("powershell Get-Clipboard", 
                           capture_output=True, 
                           shell=True)
    return result.stdout.decode().strip()

# ====================
# Service Management
# ====================

def start_service(service_name: str) -> bool:
    """Start a Windows service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        True if service started successfully
    """
    result = subprocess.run(f"net start {service_name}", 
                           shell=True,
                           capture_output=True)
    return result.returncode == 0

def stop_service(service_name: str) -> bool:
    """Stop a Windows service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        True if service stopped successfully
    """
    result = subprocess.run(f"net stop {service_name}", 
                          shell=True,
                          capture_output=True)
    return result.returncode == 0

def restart_service(service_name: str) -> bool:
    """Restart a Windows service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        True if service restarted successfully
    """
    return stop_service(service_name) and start_service(service_name)

# ====================
# Window Management
# ====================

def maximize_window(window_title: str) -> None:
    """Maximize window by title.
    
    Args:
        window_title: Partial window title text
    """
    subprocess.run(f'''powershell -command "$wshell = New-Object -ComObject wscript.shell; 
                    $wshell.AppActivate('{window_title}'); 
                    $wshell.SendKeys('% ')"''', shell=True)

def minimize_window(window_title: str) -> None:
    """Minimize window by title.
    
    Args:
        window_title: Partial window title text
    """
    subprocess.run(f'''powershell -command "$wshell = New-Object -ComObject wscript.shell; 
                    $wshell.AppActivate('{window_title}'); 
                    $wshell.SendKeys('% ')"''', shell=True)

# ====================
# Additional Utilities
# ====================

def set_wallpaper(image_path: str) -> None:
    """Set desktop wallpaper.
    
    Args:
        image_path: Path to image file
    """
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

def get_system_language() -> str:
    """Get system default language.
    
    Returns:
        Language code (e.g. en-US)
    """
    import locale
    windll = ctypes.windll.kernel32
    return locale.windows_locale[windll.GetUserDefaultUILanguage()]

def check_admin_rights() -> bool:
    """Check if running with administrator privileges.
    
    Returns:
        True if process has admin rights
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def empty_recycle_bin() -> None:
    """Empty the system recycle bin."""
    subprocess.run("rd /s /q C:\\$Recycle.bin", shell=True)

def get_system_uptime() -> float:
    """Get system uptime in seconds.
    
    Returns:
        Uptime duration in seconds
    """
    import time
    return time.time() - psutil.boot_time()

# ====================
# Security Utilities
# ====================

def disable_task_manager(enable: bool = False) -> None:
    """Enable/disable Windows Task Manager.
    
    Args:
        enable: True to enable, False to disable
    """
    value = "0" if enable else "1"
    key = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
    add_registry_key(key, "DisableTaskMgr", value)

def toggle_registry_editor(enable: bool = False) -> None:
    """Enable/disable Registry Editor access.
    
    Args:
        enable: True to enable, False to disable
    """
    value = "0" if enable else "1"
    key = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
    add_registry_key(key, "DisableRegistryTools", value)

import os
import sys
import time
import ctypes
import winreg
import socket
import struct
import platform
import win32api
import win32con
import win32security
from typing import Optional, List, Dict

# ========================
# Environment Variables
# ========================

def set_environment_variable(name: str, value: str) -> None:
    """Set persistent environment variable for current user.
    
    Args:
        name: Variable name
        value: Variable value
    """
    winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Environment")
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Environment",
        0, 
        winreg.KEY_WRITE
    ) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
    win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')

def delete_environment_variable(name: str) -> None:
    """Delete user environment variable.
    
    Args:
        name: Variable name to delete
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0, 
            winreg.KEY_WRITE
        ) as key:
            winreg.DeleteValue(key, name)
        win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
    except FileNotFoundError:
        pass

# ========================
# User Account Management
# ========================

def get_current_user() -> str:
    """Get current logged in username.
    
    Returns:
        username in DOMAIN\\USER format
    """
    return win32api.GetUserNameEx(win32con.NameSamCompatible)

def list_local_users() -> List[str]:
    """List all local user accounts.
    
    Returns:
        List of usernames
    """
    import win32net
    users = []
    i = 0
    while True:
        try:
            user = win32net.NetUserEnum(None, 0, i)[0]
            users.append(user['name'])
            i += 1
        except:
            break
    return users

# ========================
# Hardware Information
# ========================

def get_gpu_info() -> List[Dict]:
    """Get GPU information using WMI.
    
    Returns:
        List of GPUs with name and memory info
    """
    import wmi
    w = wmi.WMI()
    return [{
        'name': gpu.Name,
        'memory_total': gpu.AdapterRAM
    } for gpu in w.Win32_VideoController()]

def get_bios_info() -> Dict:
    """Get BIOS information.
    
    Returns:
        Dictionary with BIOS details
    """
    import wmi
    w = wmi.WMI()
    bios = w.Win32_BIOS()[0]
    return {
        'manufacturer': bios.Manufacturer,
        'version': bios.SMBIOSBIOSVersion,
        'release_date': bios.ReleaseDate
    }

# ========================
# Power Management
# ========================

def set_power_plan(plan_guid: str) -> bool:
    """Activate specific power plan.
    
    Args:
        plan_guid: GUID of power plan
        
    Returns:
        True if successful
    """
    result = subprocess.run(
        f"powercfg /SETACTIVE {plan_guid}",
        shell=True,
        capture_output=True
    )
    return result.returncode == 0

def get_active_power_plan() -> Dict:
    """Get current power plan details.
    
    Returns:
        Dictionary with power plan info
    """
    result = subprocess.run(
        "powercfg /GETACTIVESCHEME",
        shell=True,
        capture_output=True,
        text=True
    )
    output = result.stdout.split()
    return {
        'guid': output[3],
        'name': ' '.join(output[4:])
    }

# ========================
# System Configuration
# ========================

def enable_remote_desktop(enable: bool = True) -> None:
    """Enable/disable Remote Desktop.
    
    Args:
        enable: True to enable, False to disable
    """
    value = 1 if enable else 0
    key_path = r"SYSTEM\CurrentControlSet\Control\Terminal Server"
    with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        key_path,
        0,
        winreg.KEY_WRITE
    ) as key:
        winreg.SetValueEx(key, "fDenyTSConnections", 0, winreg.REG_DWORD, value)

def set_system_time(new_time: time.struct_time) -> None:
    """Set system clock time.
    
    Args:
        new_time: Time tuple (struct_time)
    """
    win32api.SetSystemTime(
        new_time.tm_year, new_time.tm_mon, new_time.tm_wday,
        new_time.tm_mday, new_time.tm_hour, new_time.tm_min,
        new_time.tm_sec, 0
    )

# ========================
# Security & Permissions
# ========================

def take_ownership(file_path: str) -> None:
    """Take ownership of a file/folder.
    
    Args:
        file_path: Target file/directory
    """
    # 需要管理员权限
    SD = win32security.SECURITY_DESCRIPTOR()
    SD.Initialize()
    user, _, _ = win32security.LookupAccountName("", win32api.GetUserName())
    SD.SetSecurityDescriptorOwner(user, False)
    win32security.SetFileSecurity(
        file_path,
        win32security.OWNER_SECURITY_INFORMATION,
        SD
    )

def set_file_permission(file_path: str, sid: str, permissions: int) -> None:
    """Set file permissions for specific SID.
    
    Args:
        file_path: Target file/directory
        sid: Security Identifier
        permissions: Combination of win32con.FILE_GENERIC_*
    """
    sd = win32security.GetFileSecurity(
        file_path, win32security.DACL_SECURITY_INFORMATION
    )
    dacl = win32security.ACL()
    dacl.AddAccessAllowedAce(
        win32security.ACL_REVISION,
        permissions,
        win32security.ConvertStringSidToSid(sid)
    )
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(
        file_path,
        win32security.DACL_SECURITY_INFORMATION,
        sd
    )

# ========================
# System Logs & Events
# ========================

def get_system_events(last_hours: int = 24) -> List[Dict]:
    """Retrieve system events from Event Log.
    
    Args:
        last_hours: Lookback period
        
    Returns:
        List of event dictionaries
    """
    import win32evtlog
    events = []
    hand = win32evtlog.OpenEventLog(None, "System")
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    cutoff = time.time() - last_hours*3600
    
    while True:
        records = win32evtlog.ReadEventLog(hand, flags, 0)
        if not records:
            break
            
        for r in records:
            if r.TimeGenerated.timestamp() < cutoff:
                return events
            events.append({
                'time': r.TimeGenerated,
                'source': r.SourceName,
                'event_id': r.EventID,
                'message': r.StringInserts
            })
    
    win32evtlog.CloseEventLog(hand)
    return events

# ========================
# Device Management
# ========================

def list_connected_usb() -> List[Dict]:
    """List connected USB devices.
    
    Returns:
        List of USB device info
    """
    import wmi
    w = wmi.WMI()
    return [{
        'description': dev.Description,
        'manufacturer': dev.Manufacturer,
        'device_id': dev.DeviceID
    } for dev in w.Win32_USBControllerDevice()]

def disable_device(device_id: str) -> bool:
    """Disable a hardware device.
    
    Args:
        device_id: Device instance ID
        
    Returns:
        True if successful
    """
    result = subprocess.run(
        f'pnputil /disable-device "{device_id}"',
        shell=True,
        capture_output=True
    )
    return result.returncode == 0

# ========================
# Advanced Network
# ========================

def flush_dns_cache() -> None:
    """Flush DNS resolver cache."""
    subprocess.run("ipconfig /flushdns", shell=True)

def set_dns_servers(interface: str, dns_servers: List[str]) -> bool:
    """Set DNS servers for network interface.
    
    Args:
        interface: Interface name
        dns_servers: List of DNS server IPs
        
    Returns:
        True if successful
    """
    cmd = f'netsh interface ip set dns "{interface}" static {dns_servers[0]}'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        return False
        
    for server in dns_servers[1:]:
        cmd = f'netsh interface ip add dns "{interface}" {server} index=2'
        if subprocess.run(cmd, shell=True).returncode != 0:
            return False
    return True

# ========================
# System Restore
# ========================

def create_restore_point(description: str) -> bool:
    """Create system restore point.
    
    Args:
        description: Restore point description
        
    Returns:
        True if successful
    """
    import win32com.client
    sr = win32com.client.Dispatch("SRClient.SRClient")
    return sr.SRCreateRestorePoint(description, 0, 7) == 0

# ========================
# File System Advanced
# ========================

def get_file_owner(file_path: str) -> str:
    """Get file/folder owner.
    
    Returns:
        Owner username
    """
    sd = win32security.GetFileSecurity(
        file_path, win32security.OWNER_SECURITY_INFORMATION
    )
    sid = sd.GetSecurityDescriptorOwner()
    name, domain, _ = win32security.LookupAccountSid(None, sid)
    return f"{domain}\\{name}"

def enable_ntfs_compression(file_path: str) -> None:
    """Enable NTFS compression for file/folder."""
    win32api.SetFileAttributes(file_path, win32con.FILE_ATTRIBUTE_COMPRESSED)

# ========================
# System Drivers
# ========================

def list_loaded_drivers() -> List[Dict]:
    """List loaded kernel drivers.
    
    Returns:
        List of driver info
    """
    import wmi
    w = wmi.WMI()
    return [{
        'name': d.Name,
        'state': d.State,
        'status': d.Status
    } for d in w.Win32_SystemDriver()]

# ========================
# Virtualization
# ========================

def check_virtualization_enabled() -> bool:
    """Check if CPU virtualization is enabled."""
    result = subprocess.run(
        "systeminfo",
        capture_output=True,
        text=True,
        shell=True
    )
    return "Virtualization Enabled In Firmware: Yes" in result.stdout

# ========================
# System Fonts
# ========================

def install_font(font_path: str) -> None:
    """Install font to system fonts directory."""
    fonts_dir = os.path.join(
        os.environ['WINDIR'],
        'Fonts'
    )
    shutil.copy(font_path, fonts_dir)
    win32api.SendMessage(
        win32con.HWND_BROADCAST,
        win32con.WM_FONTCHANGE,
        0,
        0
    )

# ========================
# Advanced System Control
# ========================

def enable_windows_feature(feature_name: str) -> bool:
    """Enable Windows optional feature.
    
    Args:
        feature_name: Feature ID (e.g. TelnetClient)
        
    Returns:
        True if successful
    """
    result = subprocess.run(
        f"DISM /Online /Enable-Feature /FeatureName:{feature_name} /NoRestart",
        shell=True,
        capture_output=True
    )
    return result.returncode == 0

def set_secure_boot(state: bool) -> None:
    """Enable/disable UEFI Secure Boot (requires reboot)."""
    val = "on" if state else "off"
    subprocess.run(
        f"bcdedit /set {{current}} testsigning {val}",
        shell=True
    )

# ========================
# System Encryption
# ========================

def get_bitlocker_status(drive: str = "C:") -> Dict:
    """Get BitLocker encryption status.
    
    Returns:
        Dictionary with encryption status
    """
    result = subprocess.run(
        f"manage-bde -status {drive}",
        shell=True,
        capture_output=True,
        text=True
    )
    return {
        'encrypted': "Fully Encrypted" in result.stdout,
        'protection': "Protection On" in result.stdout
    }

# ========================
# System Monitoring
# ========================

def monitor_process_creation() -> None:
    """Real-time process creation monitoring."""
    import wmi
    c = wmi.WMI()
    process_watcher = c.Win32_Process.watch_for("creation")
    while True:
        new_process = process_watcher()
        print(f"New process: {new_process.Caption} (PID: {new_process.ProcessId})")

# ========================
# System Cleanup
# ========================

def clean_temp_files() -> int:
    """Delete temporary files and return count."""
    temp_dirs = [
        os.environ['TEMP'],
        r"C:\Windows\Temp",
        r"C:\Windows\Prefetch"
    ]
    count = 0
    for d in temp_dirs:
        for root, _, files in os.walk(d):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                    count +=1
                except:
                    continue
    return count

# ========================
# Advanced UI Control
# ========================

def disable_desktop_icons() -> None:
    """Hide all desktop icons."""
    subprocess.run(
        'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer" '
        '/v "NoDesktop" /t REG_DWORD /d 1 /f',
        shell=True
    )
    subprocess.run("taskkill /f /im explorer.exe", shell=True)
    subprocess.run("start explorer.exe", shell=True)

# ========================
# System Configuration
# ========================

def set_pagefile_size(min_size: int, max_size: int) -> None:
    """Configure virtual memory/pagefile settings.
    
    Args:
        min_size: Minimum size in MB
        max_size: Maximum size in MB
    """
    cmd = (
        f"wmic pagefileset where name='C:\\\\pagefile.sys' "
        f"set InitialSize={min_size},MaximumSize={max_size}"
    )
    subprocess.run(cmd, shell=True)

# ========================
# System Information
# ========================

def get_uefi_info() -> Dict:
    """Get UEFI/BIOS information."""
    import wmi
    w = wmi.WMI(namespace='root\\wmi')
    bios = w.MS_SystemInformation()[0]
    return {
        'vendor': bios.SystemManufacturer,
        'version': bios.BIOSVersion,
        'date': bios.BIOSReleaseDate
    }

# ========================
# Advanced Security
# ========================

def configure_firewall_rule(
    name: str,
    action: str = "allow",
    protocol: str = "TCP",
    port: int = None,
    enable: bool = True
) -> bool:
    """Create/modify Windows firewall rule.
    
    Args:
        name: Rule name
        action: allow/block
        protocol: TCP/UDP
        port: Target port
        enable: Enable rule
        
    Returns:
        True if successful
    """
    cmd = [
        "netsh advfirewall firewall add rule",
        f'name="{name}"',
        f"dir=in",
        f"action={action}",
        f"protocol={protocol}",
    ]
    if port:
        cmd.append(f"localport={port}")
    cmd.append(f"enable={'yes' if enable else 'no'}")
    
    result = subprocess.run(
        " ".join(cmd),
        shell=True,
        capture_output=True
    )
    return result.returncode == 0

# ========================
# Virtual Machine Detection
# ========================

import uuid, re
import platform
import subprocess
from typing import Optional

def get_mac_address(interface: Optional[str] = None) -> Optional[str]:
    """获取指定网络接口的MAC地址
    
    Args:
        interface: 可选网络接口名称（如"eth0"）
        
    Returns:
        MAC地址字符串（如"00:1A:2B:3C:4D:5E"）或None
    """
    system = platform.system()
    
    # Windows系统
    if system == "Windows":
        cmd = "getmac /v /FO CSV"
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        for line in result.stdout.splitlines()[1:]:  # 跳过标题行
            parts = line.strip('"').split('","')
            if not interface or interface.lower() == parts[0].lower():
                return parts[-1].replace("-", ":")
        return None
    
    # Linux/macOS系统
    elif system in ["Linux", "Darwin"]:
        from netifaces import ifaddresses, AF_LINK
        iface = interface or next(iter(ifaddresses.keys()), None)
        try:
            return ifaddresses(iface)[AF_LINK][0]['addr']
        except (ValueError, KeyError):
            return None
    
    # 其他系统通过UUID生成
    return ":".join(re.findall("..", "%012x" % uuid.getnode()))

def check_virtual_machine() -> bool:
    """Detect if running in virtual machine."""
    checks = [
        # Check common VM vendor strings
        any(s in platform.platform().upper() for s in ["VIRTUAL", "VMWARE", "XEN", "KVM"]),
        # Check MAC address OUI
        any(oui in ":".join(get_mac_address().split(":")[:3]) for oui in ["00:05:69", "00:0C:29"]),
        # Check hypervisor present
        "hypervisor" in platform.platform().lower()
    ]
    return any(checks)

# ========================
# System Timezone
# ========================

def set_timezone(tz_id: str) -> bool:
    """Set system timezone.
    
    Args:
        tz_id: Timezone ID (e.g. "China Standard Time")
        
    Returns:
        True if successful
    """
    result = subprocess.run(
        f'tzutil /s "{tz_id}"',
        shell=True,
        capture_output=True
    )
    return result.returncode == 0

# ========================
# Advanced Hardware
# ========================

def get_smart_drive_info(drive: str = "0") -> Dict:
    """Retrieve S.M.A.R.T drive health data.
    
    Args:
        drive: Physical drive number
        
    Returns:
        SMART attributes dictionary
    """
    import smartmontools # type: ignore
    smart = smartmontools.SmartCtl()
    data = smart.device(f"/dev/pd{drive}").all()
    return {
        'health': data['smart_status']['passed'],
        'attributes': {
            attr['name']: attr['raw']['value']
            for attr in data['ata_smart_attributes']['table']
        }
    }

import os
import sys
import platform
import subprocess
from multiprocessing import Process
import psutil
import time
from typing import Optional, Tuple

# ====================== 屏幕亮度控制 ======================
def SetBrightness(level: int) -> None:
    """
    设置屏幕亮度 (0-100)
    平台支持: Windows/macOS/Linux
    """
    system = platform.system()
    try:
        if not 0 <= level <= 100:
            raise ValueError("亮度值必须在0-100之间")

        if system == "Windows":
            import wmi
            c = wmi.WMI(namespace='wmi')
            methods = c.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(level, 0)
        
        elif system == "Darwin":  # macOS
            subprocess.run([
                "brightness",
                str(level / 100)
            ], check=True)
        
        elif system == "Linux":
            backlight_path = "/sys/class/backlight/"
            if not os.path.exists(backlight_path):
                raise FileNotFoundError("背光控制接口不存在")
            
            controller = os.listdir(backlight_path)[0]
            brightness_path = os.path.join(backlight_path, controller, "brightness")
            max_path = os.path.join(backlight_path, controller, "max_brightness")

            with open(max_path) as f:
                max_brightness = int(f.read().strip())
            
            value = int((level / 100) * max_brightness)
            with open(brightness_path, "w") as f:
                f.write(str(value))
        
        else:
            raise NotImplementedError(f"不支持的操作系统: {system}")
    
    except Exception as e:
        print(f"亮度设置失败: {str(e)}")

# ====================== 声音控制 ======================
class VolumeController:
    @staticmethod
    def set_volume(level: int) -> None:
        system = platform.system()
        try:
            if system == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL  # 确保导入CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level/100, None)
                
            elif system == "Darwin":
                applescript = f"set volume output volume {level}"
                subprocess.run(["osascript", "-e", applescript], check=True)
            
            elif system == "Linux":
                import alsaaudio
                mixer = alsaaudio.Mixer()
                mixer.setvolume(level)
            
            else:
                raise NotImplementedError(f"不支持的操作系统: {system}")
        
        except Exception as e:
            print(f"音量设置失败: {str(e)}")


    @staticmethod
    def get_volume() -> int:
        system = platform.system()
        try:
            if system == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))  # 添加类型转换
                return round(volume.GetMasterVolumeLevelScalar() * 100)
            
            elif system == "Darwin":
                cmd = "osascript -e 'output volume of (get volume settings)'"
                return int(subprocess.check_output(cmd, shell=True).decode().strip())
            
            elif system == "Linux":
                import alsaaudio
                mixer = alsaaudio.Mixer()
                return mixer.getvolume()[0]
            
            else:
                raise NotImplementedError(f"不支持的操作系统: {system}")
        
        except Exception as e:
            print(f"获取音量失败: {str(e)}")
            return 0

    @staticmethod
    def mute(status: bool = True) -> None:
        """静音控制"""
        system = platform.system()
        try:
            if system == "Windows":
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                interface.SetMute(1 if status else 0, None)
            
            elif system == "Darwin":
                state = "true" if status else "false"
                subprocess.run(
                    ["osascript", "-e", f"set volume with muted {state}"], check=True)
            
            elif system == "Linux":
                import alsaaudio
                mixer = alsaaudio.Mixer()
                mixer.setmute(1 if status else 0)
            
            else:
                raise NotImplementedError(f"不支持的操作系统: {system}")
        
        except Exception as e:
            print(f"静音操作失败: {str(e)}")

# ====================== 增强版进程类 ======================
class EnhancedProcess(Process):
    """
    支持两种使用模式的增强进程类：
    1. 直接实例化使用: EnhancedProcess(target=...)
    2. 继承使用: class MyProcess(EnhancedProcess)
    
    新增功能：
    - 进程资源监控 (CPU/内存)
    - 进程树终止
    - 运行时间统计
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self._start_time: Optional[float] = None
        self._pid: Optional[int] = None  # 进程PID跟踪
        self._terminated: bool = False    # 终止状态标记

    def start(self) -> None:
        """启动进程并记录元数据"""
        super().start()
        self._pid = self.pid
        self._start_time = time.time()
        self._terminated = False

    def run(self) -> None:
        """默认执行用户传入的target函数"""
        if self._target:
            self._target(*self._args, **self._kwargs)

    def get_cpu_usage(self) -> float:
        """获取当前CPU使用率 (%)"""
        if self._pid is None or self._terminated:
            return 0.0
        
        try:
            process = psutil.Process(self._pid)
            return process.cpu_percent(interval=0.1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def get_memory_usage(self) -> float:
        """获取内存使用量 (MB)"""
        if self._pid is None or self._terminated:
            return 0.0
        
        try:
            process = psutil.Process(self._pid)
            return process.memory_info().rss / (1024 ** 2)  # 转换为MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def terminate_tree(self) -> None:
        """终止进程及其所有子进程"""
        if self._pid is None or self._terminated:
            return
        
        try:
            main_process = psutil.Process(self._pid)
            children = main_process.children(recursive=True)
            
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    continue
            
            main_process.terminate()
            self._terminated = True
        
        except psutil.NoSuchProcess:
            pass

    def get_uptime(self) -> float:
        """获取进程运行时间 (秒)"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    @property
    def status(self) -> Tuple[str, float]:
        """获取进程状态摘要 (状态, 运行时间)"""
        if self._pid is None:
            return ("未启动", 0.0)
        
        try:
            process = psutil.Process(self._pid)
            return (
                process.status(),
                self.get_uptime()
            )
        except psutil.NoSuchProcess:
            return ("已终止", self.get_uptime())

# ====================== 使用示例 ======================
if __name__ == "__main__":
    # 测试亮度控制
    SetBrightness(75)
    print("已设置屏幕亮度到75%")

    # 测试音量控制
    VolumeController.set_volume(50)
    print(f"当前音量: {VolumeController.get_volume()}%")
    VolumeController.mute(False)

    # 测试进程类 (直接使用模式)
    def demo_task():
        print("直接模式进程启动")
        time.sleep(2)
        print("直接模式进程结束")

    p1 = EnhancedProcess(target=demo_task)
    p1.start()
    print(f"进程状态: {p1.status[0]}, 运行时间: {p1.status[1]:.1f}s")
    p1.join()

    # 测试进程类 (继承使用模式)
    class CounterProcess(EnhancedProcess):
        def __init__(self, interval: float):
            super().__init__(daemon=True)
            self.interval = interval
        
        def run(self):
            counter = 0
            while True:
                print(f"计数器: {counter}")
                counter += 1
                time.sleep(self.interval)

    p2 = CounterProcess(0.5)
    p2.start()
    
    # 监控进程资源
    for _ in range(3):
        print(f"CPU使用: {p2.get_cpu_usage()}% | 内存使用: {p2.get_memory_usage():.1f}MB")
        time.sleep(1)
    
    p2.terminate_tree()
    print("进程已终止")