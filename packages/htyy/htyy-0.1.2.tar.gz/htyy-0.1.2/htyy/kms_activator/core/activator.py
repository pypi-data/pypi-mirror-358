import os
import re
import winreg
from .utils import run_command, logger
from .config import config

class Activator:
    def __init__(self):
        self.server_ip = config.get('kms_server')
        self.port = config.get('kms_port')
        self.kms_address = f"{self.server_ip}:{self.port}"
    
    def activate_windows(self):
        """激活Windows系统"""
        logger.info("Activating Windows...")
        
        # 设置KMS服务器
        cmd = ['cscript', '//Nologo', os.path.expandvars('%SystemRoot%\\System32\\slmgr.vbs'), 
               '/skms', self.kms_address]
        retcode, stdout, stderr = run_command(cmd, admin=True)
        
        if retcode != 0:
            logger.error(f"Failed to set KMS server: {stderr or stdout}")
            return False
        
        # 激活Windows
        cmd = ['cscript', '//Nologo', os.path.expandvars('%SystemRoot%\\System32\\slmgr.vbs'), '/ato']
        retcode, stdout, stderr = run_command(cmd, admin=True)
        
        if retcode == 0 and "successfully" in stdout:
            logger.info("Windows activated successfully")
            return True
        else:
            logger.error(f"Windows activation failed: {stderr or stdout}")
            return False
    
    def get_office_installations(self):
        """获取已安装的Office版本"""
        office_versions = []
        
        try:
            # 查找32位Office
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Microsoft\Office")
            
            for i in range(winreg.QueryInfoKey(key)[0]):
                version = winreg.EnumKey(key, i)
                if re.match(r"\d+\.\d+", version):
                    try:
                        subkey = winreg.OpenKey(key, f"{version}\\Common\\InstallRoot")
                        path = winreg.QueryValueEx(subkey, "Path")[0]
                        office_versions.append({
                            "version": version,
                            "path": path,
                            "bitness": "32-bit"
                        })
                    except:
                        continue
        
        except FileNotFoundError:
            pass
        
        try:
            # 查找64位Office
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\WOW6432Node\Microsoft\Office")
            
            for i in range(winreg.QueryInfoKey(key)[0]):
                version = winreg.EnumKey(key, i)
                if re.match(r"\d+\.\d+", version):
                    try:
                        subkey = winreg.OpenKey(key, f"{version}\\Common\\InstallRoot")
                        path = winreg.QueryValueEx(subkey, "Path")[0]
                        office_versions.append({
                            "version": version,
                            "path": path,
                            "bitness": "64-bit"
                        })
                    except:
                        continue
        
        except FileNotFoundError:
            pass
        
        return office_versions
    
    def activate_office(self, version=None):
        """激活Microsoft Office"""
        logger.info("Activating Microsoft Office...")
        
        installations = self.get_office_installations()
        if not installations:
            logger.error("No Office installations found")
            return False
        
        # 如果未指定版本，激活所有找到的Office
        if not version:
            success = True
            for office in installations:
                if not self._activate_single_office(office):
                    success = False
            return success
        
        # 激活指定版本的Office
        for office in installations:
            if office["version"] == version:
                return self._activate_single_office(office)
        
        logger.error(f"Office version {version} not found")
        return False
    
    def _activate_single_office(self, office_info):
        """激活单个Office安装"""
        version = office_info["version"]
        path = office_info["path"]
        bitness = office_info["bitness"]
        
        logger.info(f"Activating Office {version} ({bitness}) at {path}")
        
        # 查找ospp.vbs脚本
        ospp_path = os.path.join(path, "OSPP.VBS")
        if not os.path.exists(ospp_path):
            logger.error(f"ospp.vbs not found in {path}")
            return False
        
        # 设置KMS服务器
        cmd = ['cscript', '//Nologo', ospp_path, '/sethst:', self.server_ip]
        retcode, stdout, stderr = run_command(cmd, admin=True)
        
        if retcode != 0:
            logger.error(f"Failed to set KMS server for Office: {stderr or stdout}")
            return False
        
        # 激活Office
        cmd = ['cscript', '//Nologo', ospp_path, '/act']
        retcode, stdout, stderr = run_command(cmd, admin=True)
        
        if retcode == 0 and "successful" in stdout:
            logger.info(f"Office {version} activated successfully")
            return True
        else:
            logger.error(f"Office activation failed: {stderr or stdout}")
            return False
    
    def check_activation_status(self):
        """检查激活状态"""
        results = {}
        
        # 检查Windows激活状态
        cmd = ['cscript', '//Nologo', os.path.expandvars('%SystemRoot%\\System32\\slmgr.vbs'), '/xpr']
        retcode, stdout, stderr = run_command(cmd)
        
        if retcode == 0:
            results['windows'] = stdout.strip()
        else:
            results['windows'] = f"Error: {stderr or stdout}"
        
        # 检查Office激活状态
        installations = self.get_office_installations()
        office_status = {}
        
        for office in installations:
            ospp_path = os.path.join(office["path"], "OSPP.VBS")
            if os.path.exists(ospp_path):
                cmd = ['cscript', '//Nologo', ospp_path, '/dstatus']
                retcode, stdout, stderr = run_command(cmd)
                
                if retcode == 0:
                    # 提取激活信息
                    status = "Not activated"
                    if "---LICENSED---" in stdout:
                        status = "Activated"
                    elif "---NOTIFICATIONS---" in stdout:
                        status = "Grace period"
                    
                    office_status[office["version"]] = status
                else:
                    office_status[office["version"]] = f"Error: {stderr or stdout}"
        
        results['office'] = office_status
        
        return results