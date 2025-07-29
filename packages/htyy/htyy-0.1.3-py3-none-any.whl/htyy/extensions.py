"""
HTTP 扩展模块 - extensions.py
功能: 缓存控制、国际化、日志、重试策略等高级功能
版本: 1.3.0
"""

import time
import json
import logging
import hashlib
from functools import wraps
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable

# ==================== 缓存系统 ====================
class LRUCache:
    """LRU 缓存实现 (最近最少使用策略)"""
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[bytes]:
        if key not in self.cache:
            self.misses += 1
            return None
        
        value = self.cache.pop(key)
        self.cache[key] = value
        self.hits += 1
        return value["data"]

    def set(self, key: str, value: bytes, ttl: int = 300) -> None:
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = {
            "data": value,
            "expire": datetime.now() + timedelta(seconds=ttl)
        }

    def clear_expired(self) -> int:
        """清理过期缓存并返回清理数量"""
        count = 0
        now = datetime.now()
        for key in list(self.cache.keys()):
            if self.cache[key]["expire"] < now:
                del self.cache[key]
                count += 1
        return count

# ==================== 国际化支持 ====================
class I18NManager:
    """国际化资源管理器"""
    def __init__(self, locale: str = "en_US"):
        self.locale = locale
        self._translations: Dict[str, Dict[str, str]] = {
            "en_US": self._load_default_english(),
            "zh_CN": self._load_default_chinese()
        }

    def translate(self, msg_key: str, **kwargs) -> str:  # 参数重命名
        """获取本地化字符串"""
        template = self._translations[self.locale].get(msg_key, msg_key)
        return template.format(**kwargs)

    def add_locale(self, locale: str, strings: Dict[str, str]) -> None:
        """添加自定义语言包"""
        self._translations[locale] = strings

    @staticmethod
    def _load_default_english() -> Dict[str, str]:
        return {
            "cache_hit": "Cache hit: {cache_key}",
            "cache_miss": "Cache miss: {cache_key}",
            "retry_attempt": "Attempt {attempt}/{max} after {delay:.1f}s"
        }

    @staticmethod
    def _load_default_chinese() -> Dict[str, str]:
        return {
            "cache_hit": "缓存命中: {cache_key}",
            "cache_miss": "缓存未命中: {cache_key}",
            "retry_attempt": "第 {attempt}/{max} 次重试 (等待 {delay:.1f} 秒)"
        }

# ==================== 日志系统 ====================
class HttpLogger:
    """HTTP 请求日志记录器"""
    def __init__(self, name: str = "HTTP_CLIENT"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加 handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_request(self, request) -> None:
        """记录请求信息"""
        self.logger.info(
            "[Request] %s %s Headers: %s",
            request.method,
            request.url,
            json.dumps(dict(request.headers))
        )

    def log_response(self, response) -> None:
        """记录响应信息"""
        self.logger.info(
            "[Response] %d %s Size: %dB Time: %.2fs",
            response.status_code,
            response.reason,
            len(response.content),
            response.elapsed.total_seconds()
        )

# ==================== 重试策略 ====================
class RetryPolicy:
    """智能重试策略控制器"""
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: tuple = (500, 502, 503, 504)
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist

    def should_retry(self, response) -> bool:
        """判断是否需要重试"""
        if response.status_code in self.status_forcelist:
            return True
        # 可以在此添加更多重试条件
        return False

    def get_retry_delay(self, attempt: int) -> float:
        """计算退避延迟时间"""
        return min(self.backoff_factor * (2 ** (attempt - 1)), 10)

# ==================== 高级功能装饰器 ====================
def cacheable(ttl: int = 300):
    """请求缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # 生成唯一缓存键
            cache_key = hashlib.md5(json.dumps({
                "method": request.method,
                "url": request.url,
                "params": request.params,
                "data": request.data
            }).encode()).hexdigest()

            # 尝试获取缓存
            if request.cache and (cached := request.cache.get(cache_key)):
                request.logger.info(
                    request.i18n.translate("cache_hit", key=cache_key)
                )
                return cached

            # 执行实际请求
            response = func(request, *args, **kwargs)

            # 缓存有效响应
            if response.status_code == 200:
                request.cache.set(cache_key, response.content, ttl=ttl)
                request.logger.info(
                    request.i18n.translate("cache_miss", key=cache_key)
                )
            
            return response
        return wrapper
    return decorator

def retryable(policy: RetryPolicy = RetryPolicy()):
    """请求重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            attempt = 1
            while attempt <= policy.max_retries:
                response = func(request, *args, **kwargs)
                
                if not policy.should_retry(response):
                    return response
                
                delay = policy.get_retry_delay(attempt)
                request.logger.warning(
                    request.i18n.translate(
                        "retry_attempt",
                        attempt=attempt,
                        max=policy.max_retries,
                        delay=delay
                    )
                )
                time.sleep(delay)
                attempt += 1
            
            return response
        return wrapper
    return decorator

# ==================== 单元测试 ====================
if __name__ == "__main__":
    # 初始化组件
    cache = LRUCache()
    i18n = I18NManager("zh_CN")
    logger = HttpLogger()
    retry_policy = RetryPolicy()

    # 测试缓存系统
    cache.set("test", b"hello", ttl=10)
    assert cache.get("test") == b"hello"

    # 测试代码修改后
    assert "缓存命中" in i18n.translate("cache_hit", cache_key="test")

    # 测试日志系统
    class MockRequest:
        method = "GET"
        url = "http://example.com"
        headers = {"User-Agent": "Test"}
    
    logger.log_request(MockRequest())