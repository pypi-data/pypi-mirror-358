import os
import subprocess
import time
import threading
from .utils import run_command, get_vlmcsd_path, logger
from .config import config

class KMSServer:
    def __init__(self):
        self.process = None
        self.port = config.get('kms_port')
        self.server_ip = config.get('kms_server')
        self.vlmcsd_path = get_vlmcsd_path()
        self.is_running = False
    
    def start(self, background=True):
        """启动KMS服务器"""
        if not self.vlmcsd_path:
            logger.error("vlmcsd not found. Please install it first.")
            return False
        
        if self.is_running:
            logger.info("KMS server is already running")
            return True
        
        try:
            cmd = [self.vlmcsd_path, "-e", "-v", "-p", str(self.port)]
            
            if background:
                # 在后台运行
                if os.name == 'nt':  # Windows
                    self.process = subprocess.Popen(
                        cmd, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:  # Linux/Mac
                    self.process = subprocess.Popen(
                        cmd, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                
                # 检查进程是否启动成功
                time.sleep(1)
                if self.process.poll() is None:
                    self.is_running = True
                    logger.info(f"KMS server started on port {self.port}")
                    return True
                else:
                    logger.error("Failed to start KMS server")
                    return False
            else:
                # 在前台运行
                logger.info(f"Starting KMS server on port {self.port}...")
                self.process = subprocess.Popen(cmd)
                self.is_running = True
                self.process.wait()
                self.is_running = False
                return True
        except Exception as e:
            logger.error(f"Error starting KMS server: {e}")
            return False
    
    def stop(self):
        """停止KMS服务器"""
        if not self.is_running:
            logger.info("KMS server is not running")
            return True
        
        try:
            if os.name == 'nt':  # Windows
                run_command(['taskkill', '/F', '/PID', str(self.process.pid)])
            else:  # Linux/Mac
                run_command(['kill', '-9', str(self.process.pid)])
            
            self.is_running = False
            logger.info("KMS server stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping KMS server: {e}")
            return False
    
    def status(self):
        """检查KMS服务器状态"""
        if not self.is_running:
            return "Stopped"
        
        try:
            # 检查进程是否仍在运行
            if self.process.poll() is None:
                return "Running"
            else:
                self.is_running = False
                return "Stopped"
        except:
            return "Unknown"
    
    def test(self):
        """测试KMS服务器是否正常工作"""
        if not self.vlmcsd_path:
            logger.error("vlmcsd not found")
            return False
        
        cmd = [self.vlmcsd_path, "-v", "-T", self.server_ip, str(self.port)]
        retcode, stdout, stderr = run_command(cmd)
        
        if retcode == 0 and "successful" in stdout:
            logger.info("KMS server test successful")
            return True
        else:
            logger.error(f"KMS server test failed: {stderr or stdout}")
            return False