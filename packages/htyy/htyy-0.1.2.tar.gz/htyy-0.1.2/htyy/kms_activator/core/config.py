import os
import json
import platform

class Config:
    CONFIG_FILE = os.path.expanduser("~/.kms_activator/config.json")
    
    DEFAULT_CONFIG = {
        "kms_port": 1688,
        "kms_server": "127.0.0.1",
        "auto_start_server": True,
        "vlmcsd_path": "",
        "log_level": "INFO"
    }
    
    def __init__(self):
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        self.config = self._load_config()
        
    def _load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key):
        return self.config.get(key, self.DEFAULT_CONFIG.get(key, None))
    
    def set(self, key, value):
        self.config[key] = value
        self.save()
    
    @property
    def system_platform(self):
        return platform.system().lower()
    
    @property
    def architecture(self):
        arch = platform.machine().lower()
        if 'x86_64' in arch or 'amd64' in arch:
            return 'x64'
        elif 'x86' in arch or 'i386' in arch:
            return 'x86'
        elif 'arm' in arch:
            return 'arm'
        return 'unknown'
    
config = Config()