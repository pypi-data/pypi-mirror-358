"""
HTTP 客户端核心模块 - client.py
版本: 2.0.0
功能: 连接池管理、智能重试、SSL 验证、代理支持
"""

import ssl
import time
import socket
import logging
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse
from typing import Optional, Dict, Union

# ==================== 连接池实现 ====================
class ConnectionPool:
    """HTTP(S) 连接池"""
    
    def __init__(self, max_size: int = 10, idle_timeout: int = 60):
        self.max_size = max_size
        self.idle_timeout = idle_timeout
        self._pool = []
        self._in_use = set()
        self.logger = logging.getLogger("ConnectionPool")

    def get_connection(
        self,
        host: str,
        port: int,
        is_https: bool = False,
        ssl_context: Optional[ssl.SSLContext] = None
    ) -> Union[HTTPConnection, HTTPSConnection]:
        """从池中获取或创建新连接"""
        now = time.time()
        
        # 清理过期连接
        self._pool = [
            (conn, t) for conn, t in self._pool
            if (now - t) < self.idle_timeout
        ]
        
        # 查找可用连接
        for i, (conn, _) in enumerate(self._pool):
            if (
                conn.host == host and
                conn.port == port and
                isinstance(conn, HTTPSConnection if is_https else HTTPConnection)
            ):
                conn = self._pool.pop(i)[0]
                self._in_use.add(conn)
                return conn
                
        # 创建新连接
        if len(self._pool) + len(self._in_use) >= self.max_size:
            raise ConnectionError("Connection pool is full")
        
        conn_class = HTTPSConnection if is_https else HTTPConnection
        conn = conn_class(host, port, context=ssl_context)
        self._in_use.add(conn)
        return conn

    def release_connection(self, conn: Union[HTTPConnection, HTTPSConnection]):
        """释放连接回池中"""
        if conn in self._in_use:
            self._in_use.remove(conn)
            self._pool.append((conn, time.time()))
            conn.close()  # 实际生产中应保持连接打开

# ==================== 核心客户端类 ====================
class HttpClient:
    """智能 HTTP 客户端"""
    
    def __init__(
        self,
        pool_size: int = 10,
        max_retries: int = 3,
        timeout: float = 10.0,
        ssl_verify: bool = True,
        proxy: Optional[str] = None
    ):
        self.pool = ConnectionPool(max_size=pool_size)
        self.max_retries = max_retries
        self.timeout = timeout
        self.ssl_verify = ssl_verify
        self.proxy = proxy
        self.logger = logging.getLogger("HttpClient")
        self._ssl_context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """创建 SSL 上下文"""
        ctx = ssl.create_default_context()
        if not self.ssl_verify:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _prepare_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None
    ) -> tuple:
        """解析 URL 并准备连接参数"""
        parsed = urlparse(url)
        is_https = parsed.scheme == "https"
        port = parsed.port or (443 if is_https else 80)
        
        if self.proxy:
            proxy_parsed = urlparse(self.proxy)
            return (
                proxy_parsed.hostname,
                proxy_parsed.port or (443 if proxy_parsed.scheme == "https" else 80),
                True,  # 使用代理
                parsed._replace(scheme="https" if is_https else "http").geturl()
            )
            
        return (parsed.hostname, port, False, None)

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        retry_count: int = 0
    ):
        """执行 HTTP 请求"""
        host, port, use_proxy, real_url = self._prepare_request(method, url, headers, body)
        
        try:
            conn = self.pool.get_connection(
                host=host,
                port=port,
                is_https=self.ssl_verify,
                ssl_context=self._ssl_context
            )
            
            headers = headers or {}
            if use_proxy and real_url:
                conn.set_tunnel(real_url)
                
            conn.request(
                method=method.upper(),
                url=url,
                body=body,
                headers=headers
            )
            
            response = conn.getresponse()
            self.pool.release_connection(conn)
            return HttpResponse(
                status=response.status,
                headers=dict(response.getheaders()),
                body=response.read(),
                request=url
            )
            
        except (socket.timeout, ConnectionError) as e:
            self.logger.warning(f"请求失败: {str(e)}")
            if retry_count < self.max_retries:
                wait = min(2 ** retry_count, 10)
                self.logger.info(f"{wait}秒后重试...")
                time.sleep(wait)
                return self.request(method, url, headers, body, retry_count + 1)
            raise

# ==================== 响应处理类 ====================
class HttpResponse:
    """HTTP 响应封装"""
    
    def __init__(
        self,
        status: int,
        headers: Dict[str, str],
        body: bytes,
        request: str
    ):
        self.status_code = status
        self.headers = CaseInsensitiveDict(headers)
        self.content = body
        self.request_url = request
        self._text = None

    @property
    def text(self) -> str:
        """解码为文本内容"""
        if self._text is None:
            charset = self._detect_charset()
            try:
                self._text = self.content.decode(charset)
            except UnicodeDecodeError:
                self._text = self.content.decode("utf-8", errors="replace")
        return self._text

    def _detect_charset(self) -> str:
        """检测字符编码"""
        content_type = self.headers.get("Content-Type", "")
        if "charset=" in content_type:
            return content_type.split("charset=")[1].split(";")[0].strip()
        return "utf-8"

# ==================== 辅助类 ====================
class CaseInsensitiveDict(dict):
    """大小写不敏感的字典"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._keys = {k.lower(): k for k in self.keys()}
    
    def __getitem__(self, key: str):
        return super().__getitem__(self._keys[key.lower()])
    
    def get(self, key: str, default=None):
        try:
            return self[key]
        except KeyError:
            return default

# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 初始化客户端
    client = HttpClient(
        pool_size=5,
        max_retries=3,
        ssl_verify=True
    )
    
    # 发送 GET 请求
    response = client.request("GET", "https://www.example.com")
    print(f"状态码: {response.status_code}")
    print(f"响应长度: {len(response.content)} bytes")
    print(f"内容类型: {response.headers.get('Content-Type')}")