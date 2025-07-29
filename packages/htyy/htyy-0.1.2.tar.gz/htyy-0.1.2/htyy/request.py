"""
HTTP请求核心模块
版本: 1.2.0
功能: 多部分上传、连接池、重试机制、国际化等
"""

import os
import ssl
import time
import zlib
import json
import socket
import hashlib
import mimetypes
import concurrent, base64
from io import BytesIO
from urllib.parse import urlencode, urlparse, quote, unquote, parse_qs
from http.client import HTTPConnection, HTTPSConnection
from email.generator import Generator
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart

# ==================== 国际化支持 ====================
TRANSLATIONS = {
    'en_US': {
        'invalid_url': 'Invalid URL format',
        'connection_failed': 'Connection to {host} failed',
        'ssl_required': 'SSL required for HTTPS URLs',
        'proxy_error': 'Proxy connection error',
        'auth_required': 'Authentication required',
        'file_not_found': 'File "{file}" not found',
        'max_retries': 'Max retries exceeded ({max_retries} attempts)',
        'timeout': 'Request timed out after {timeout}s',
        'encoding_error': 'Content encoding error',
        'invalid_method': 'Invalid HTTP method: {method}',
        'chunked_upload': 'Chunked upload failed at {percent}%'
    },
    'zh_CN': {
        'invalid_url': 'URL格式无效',
        'connection_failed': '无法连接到{host}',
        'ssl_required': 'HTTPS URL需要SSL连接',
        'proxy_error': '代理连接错误',
        'auth_required': '需要身份验证',
        'file_not_found': '未找到文件"{file}"',
        'max_retries': '超过最大重试次数({max_retries}次)',
        'timeout': '请求超时({timeout}秒)',
        'encoding_error': '内容编码错误',
        'invalid_method': '无效的HTTP方法: {method}',
        'chunked_upload': '分块上传失败于{percent}%'
    }
}

class I18n:
    """国际化支持类"""
    def __init__(self, locale='en_US'):
        self.locale = locale
        self._strings = TRANSLATIONS.get(locale, TRANSLATIONS['en_US'])
    
    def gettext(self, key, **kwargs):
        msg = self._strings.get(key, key)
        return msg.format(**kwargs)

# ==================== 异常定义 ====================
class RequestError(Exception):
    """基础请求异常"""
    def __init__(self, message, code=None):
        self.code = code
        super().__init__(message)

class InvalidURL(RequestError):
    """无效URL异常"""

class ConnectionFailed(RequestError):
    """连接失败异常"""

class SSLError(RequestError):
    """SSL错误"""

# ==================== 核心请求类 ====================
class HttpRequest:
    """增强型HTTP请求处理器"""
    
    VALID_METHODS = {'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'PATCH', 'OPTIONS'}
    DEFAULT_TIMEOUT = 10
    CHUNK_SIZE = 1024 * 1024  # 1MB分块
    
    def __init__(self, method, url, params=None, data=None, files=None, 
                 headers=None, auth=None, timeout=None, allow_redirects=True,
                 max_retries=3, proxy=None, verify=True, cert=None, cookies=None,
                 hooks=None, i18n=None, chunked=False):
        
        # 初始化国际化
        self.i18n = i18n or I18n()
        
        self.method = method.upper()
        if self.method not in self.VALID_METHODS:
            raise RequestError(self.i18n.gettext('invalid_method', method=method))
        
        self.original_url = url
        self._parse_url(url)
        self.params = params or {}
        self.data = data
        self.files = files or {}
        self.headers = headers.copy() if headers else {}
        self.auth = auth
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.allow_redirects = allow_redirects
        self.max_retries = max_retries
        self.proxy = proxy
        self.verify = verify
        self.cert = cert
        self.cookies = cookies or {}
        self.hooks = hooks or {}
        self.chunked = chunked
        
        # 连接相关属性
        self._connection = None
        self._response = None
        self._retry_count = 0
        self._start_time = None
        
        # 自动填充头信息
        self._prepare_default_headers()
        
        # 构建请求体
        self._body = None
        self.content_length = 0
        self._build_body()
        
        # SSL上下文
        self.ssl_context = self._create_ssl_context() if self.is_https else None
        
        # 代理处理
        if self.proxy:
            self._process_proxy()
        
        # 身份验证
        if self.auth:
            self._apply_auth()
        
        # Cookie处理
        self._prepare_cookies()
    
    def _parse_url(self, url):
        """解析并验证URL"""
        try:
            parsed = urlparse(url)
            self.is_https = parsed.scheme.lower() == "https"
            if not parsed.scheme or not parsed.netloc:
                raise ValueError
        except:
            raise InvalidURL(self.i18n.gettext('invalid_url'))
        
        self.scheme = parsed.scheme
        self.host = parsed.hostname
        self.port = parsed.port or (443 if self.scheme == 'https' else 80)
        self.path = parsed.path or '/'
        self.query = parsed.query
        
        if not self.scheme.startswith('http'):
            raise InvalidURL(self.i18n.gettext('invalid_url'))
    
    def _prepare_default_headers(self):
        """准备默认请求头"""
        defaults = {
            'User-Agent': 'AdvancedHTTP/2.0',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        for k, v in defaults.items():
            if k not in self.headers:
                self.headers[k] = v
        
        if 'Host' not in self.headers:
            self.headers['Host'] = self.host
    
    def _build_query_params(self):
        """将参数编码到URL查询字符串"""
        if self.params:
            # 编码参数
            encoded_params = []
            for k, v in self.params.items():
                if isinstance(v, (list, tuple)):
                    for item in v:
                        encoded_params.append(f"{quote(k)}={quote(str(item))}")
                else:
                    encoded_params.append(f"{quote(k)}={quote(str(v))}")
            
            query = "&".join(encoded_params)
            
            # 合并到现有查询中
            if "?" in self.path:
                self.path += "&" + query
            else:
                self.path += "?" + query

    def _build_body(self):
        """构建请求体（支持多种格式）"""
        if self.method in ('GET', 'HEAD'):
            self._build_query_params()
            return
        
        if self.files:
            self._build_multipart_body()
        elif self.data is not None:
            if isinstance(self.data, (dict, list)):
                self.headers['Content-Type'] = 'application/json'
                self._body = json.dumps(self.data).encode()
            elif isinstance(self.data, bytes):
                self._body = self.data
            else:
                self._body = str(self.data).encode()
            self.headers['Content-Length'] = str(len(self._body))
        else:
            self._body = b''
            self.headers['Content-Length'] = '0'
    
    def _build_multipart_body(self):
        """构建多部分表单数据"""
        boundary = self._generate_boundary()
        self.headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        
        msg = MIMEMultipart('form-data', boundary=boundary)
        
        # 添加表单字段
        for name, value in (self.params or {}).items():
            part = MIMENonMultipart('text', 'plain')
            part['Content-Disposition'] = f'form-data; name="{name}"'
            part.set_payload(str(value))
            msg.attach(part)
        
        # 添加文件
        for name, file_info in self.files.items():
            filename = file_info.get('filename', 'file.dat')
            content = file_info.get('content')
            content_type = file_info.get('content_type') or mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            if isinstance(content, str):
                content = content.encode()
            elif hasattr(content, 'read'):
                content = content.read()
            
            part = MIMENonMultipart(*content_type.split('/', 1))
            part['Content-Disposition'] = f'form-data; name="{name}"; filename="{filename}"'
            part['Content-Transfer-Encoding'] = 'binary'
            part.set_payload(content)
            msg.attach(part)
        
        # 生成消息体
        body = BytesIO()
        gen = Generator(body, maxheaderlen=0)
        gen.flatten(msg)
        self._body = body.getvalue()
        self.headers['Content-Length'] = str(len(self._body))
    
    def _generate_boundary(self):
        """生成MIME边界字符串"""
        return hashlib.sha256(os.urandom(32)).hexdigest()[:30]
    
    def _create_ssl_context(self):
        """创建SSL上下文"""
        if not self.verify:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx
        
        ctx = ssl.create_default_context()
        if self.cert:
            if isinstance(self.cert, tuple):
                ctx.load_cert_chain(*self.cert)
            else:
                ctx.load_cert_chain(self.cert)
        return ctx
    
    def _process_proxy(self):
        """处理代理设置"""
        if not self.proxy:
            return
        
        proxy_parsed = urlparse(self.proxy)
        if proxy_parsed.scheme not in ('http', 'https'):
            raise RequestError(self.i18n.gettext('proxy_error'))
        
        self.proxy_host = proxy_parsed.hostname
        self.proxy_port = proxy_parsed.port or (443 if proxy_parsed.scheme == 'https' else 80)
        self.proxy_auth = None
        
        if proxy_parsed.username or proxy_parsed.password:
            self.proxy_auth = (proxy_parsed.username, proxy_parsed.password)
    
    def _apply_auth(self):
        """应用身份验证"""
        if isinstance(self.auth, tuple) and len(self.auth) == 2:
            from base64 import b64encode
            auth_str = f"{self.auth[0]}:{self.auth[1]}"
            self.headers['Authorization'] = f"Basic {b64encode(auth_str.encode()).decode()}"
        elif callable(self.auth):
            self.auth(self)
        else:
            raise RequestError(self.i18n.gettext('auth_required'))
    
    def _prepare_cookies(self):
        """准备Cookie头"""
        if self.cookies:
            cookie_str = '; '.join([f"{k}={v}" for k, v in self.cookies.items()])
            self.headers['Cookie'] = cookie_str
    
    def execute(self):
        """执行请求"""
        self._start_time = time.time()
        
        while self._retry_count <= self.max_retries:
            try:
                self._connect()
                self._send_request()
                return self._read_response()
            except (socket.timeout, ConnectionError) as e:
                self._retry_count += 1
                if self._retry_count > self.max_retries:
                    raise RequestError(
                        self.i18n.gettext('max_retries', max_retries=self.max_retries)
                    ) from e
                time.sleep(self._calculate_backoff())
                continue
            finally:
                if self._connection:
                    self._connection.close()
    
    def _connect(self):
        """建立连接"""
        if self.proxy:
            self._connection = self._create_proxy_connection()
        else:
            if self.scheme == 'https':
                self._connection = HTTPSConnection(
                    self.host, 
                    port=self.port,
                    timeout=self.timeout,
                    context=self.ssl_context
                )
            else:
                self._connection = HTTPConnection(
                    self.host,
                    port=self.port,
                    timeout=self.timeout
                )
        
        try:
            self._connection.connect()
        except socket.error as e:
            raise ConnectionFailed(
                self.i18n.gettext('connection_failed', host=self.host)
            ) from e
    
    def _create_proxy_connection(self):
        """创建代理连接"""
        if self.scheme == 'https':
            conn = HTTPSConnection(
                self.proxy_host,
                port=self.proxy_port,
                timeout=self.timeout,
                context=self.ssl_context
            )
        else:
            conn = HTTPConnection(
                self.proxy_host,
                port=self.proxy_port,
                timeout=self.timeout
            )
        
        if self.proxy_auth:
            from base64 import b64encode
            auth = b64encode(f"{self.proxy_auth[0]}:{self.proxy_auth[1]}".encode()).decode()
            conn.set_tunnel(self.host, self.port, {'Proxy-Authorization': f'Basic {auth}'})
        else:
            conn.set_tunnel(self.host, self.port)
        
        return conn
    
    def _send_request(self):
        """发送请求"""
        path = self.path
        if self.query:
            path += f'?{self.query}'
        
        if self.chunked and self._body:
            self.headers['Transfer-Encoding'] = 'chunked'
            self._connection.putrequest(self.method, path, skip_host=True)
            for header, value in self.headers.items():
                self._connection.putheader(header, value)
            self._connection.endheaders()
            
            # 分块发送
            total = len(self._body)
            sent = 0
            while sent < total:
                chunk = self._body[sent:sent+self.CHUNK_SIZE]
                self._connection.send(f"{len(chunk):X}\r\n".encode())
                self._connection.send(chunk)
                self._connection.send(b"\r\n")
                sent += len(chunk)
                progress = (sent / total) * 100
                if 'progress' in self.hooks:
                    self.hooks['progress'](progress)
            
            self._connection.send(b"0\r\n\r\n")
        else:
            self._connection.request(
                self.method,
                path,
                body=self._body,
                headers=self.headers
            )
    
    def _read_response(self):
        """读取响应"""
        resp = self._connection.getresponse()
        return HttpResponse(
            status=resp.status,
            headers=resp.getheaders(),
            body=resp.read(),
            request=self,
            elapsed=time.time() - self._start_time
        )
    
    def _calculate_backoff(self):
        """计算指数退避时间"""
        return min(2 ** self._retry_count * 0.5, 60)  # 最大60秒
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

# ==================== 响应类 ====================
class HttpResponse:
    """HTTP响应封装"""
    
    def __init__(self, status, headers, body, request, elapsed):
        self.status_code = status
        self.headers = dict(headers)
        self.raw_body = body
        self.request = request
        self.elapsed = elapsed
        self._content = None
        self._text = None
        self._json = None
        
        # 处理内容编码
        self._decode_content()
    
    @property
    def content(self):
        """原始二进制内容"""
        if self._content is None:
            self._content = self.raw_body
        return self._content
    
    @property
    def text(self):
        """解码后的文本内容"""
        if self._text is None:
            charset = self._detect_charset()
            try:
                self._text = self.content.decode(charset)
            except UnicodeDecodeError:
                self._text = self.content.decode('utf-8', 'replace')
        return self._text
    
    @property
    def json(self):
        """JSON解码内容"""
        if self._json is None:
            try:
                self._json = json.loads(self.text)
            except ValueError as e:
                raise RequestError(
                    self.request.i18n.gettext('encoding_error')
                ) from e
        return self._json
    
    def _decode_content(self):
        """处理内容编码"""
        encoding = self.headers.get('Content-Encoding', '').lower()
        if encoding == 'gzip':
            self._content = zlib.decompress(self.raw_body, 16+zlib.MAX_WBITS)
        elif encoding == 'deflate':
            self._content = zlib.decompress(self.raw_body)
        else:
            self._content = self.raw_body
    
    def _detect_charset(self):
        """检测字符集"""
        content_type = self.headers.get('Content-Type', '')
        if 'charset=' in content_type:
            return content_type.split('charset=')[-1].split(';')[0].strip()
        return 'utf-8'

# ==================== 工具函数 ====================
def get(url, **kwargs):
    return HttpRequest('GET', url, **kwargs).execute()

def post(url, data=None, **kwargs):
    return HttpRequest('POST', url, data=data, **kwargs).execute()

# ==================== HTTP方法封装 ====================
def put(url, data=None, **kwargs):
    """发送PUT请求"""
    return HttpRequest('PUT', url, data=data, **kwargs).execute()

def delete(url, **kwargs):
    """发送DELETE请求"""
    return HttpRequest('DELETE', url, **kwargs).execute()

def patch(url, data=None, **kwargs):
    """发送PATCH请求"""
    return HttpRequest('PATCH', url, data=data, **kwargs).execute()

def head(url, **kwargs):
    """发送HEAD请求"""
    return HttpRequest('HEAD', url, **kwargs).execute()

def options(url, **kwargs):
    """发送OPTIONS请求"""
    return HttpRequest('OPTIONS', url, **kwargs).execute()

def trace(url, **kwargs):
    """发送TRACE请求（需要服务器支持）"""
    return HttpRequest('TRACE', url, **kwargs).execute()

def connect(url, **kwargs):
    """发送CONNECT请求（通常用于代理）"""
    return HttpRequest('CONNECT', url, **kwargs).execute()

# ==================== 批量操作封装 ====================
def batch_request(requests, max_workers=5):
    """并发执行多个请求
    参数:
        requests (list): 包含HttpRequest实例的列表
        max_workers (int): 最大并发数
    返回:
        dict: {请求对象: 响应对象}
    """
    from concurrent.futures import ThreadPoolExecutor
    
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(req.execute): req
            for req in requests
        }
        for future in concurrent.futures.as_completed(future_map):
            req = future_map[future]
            try:
                results[req] = future.result()
            except Exception as e:
                results[req] = e
    return results

# ==================== 流式操作封装 ====================
def stream_get(url, chunk_size=1024, **kwargs):
    """
    流式GET请求
    用法:
        for chunk in stream_get(url):
            process(chunk)
    """
    req = HttpRequest('GET', url, **kwargs)
    response = req.execute()
    
    def chunk_generator():
        total = int(response.headers.get('Content-Length', 0))
        received = 0
        while True:
            chunk = response.raw.read(chunk_size)
            if not chunk:
                break
            received += len(chunk)
            if 'progress' in req.hooks:
                progress = (received / total) * 100 if total > 0 else 0
                req.hooks['progress'](progress)
            yield chunk
    
    return chunk_generator()

def stream_upload(url, file_path, chunk_size=1024*1024, **kwargs):
    """流式上传大文件
    参数:
        file_path (str): 要上传的文件路径
        chunk_size (int): 分块大小（字节）
    """
    def file_chunk_generator():
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    file_size = os.path.getsize(file_path)
    headers = kwargs.pop('headers', {})
    headers.update({
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(file_size),
        'X-Upload-Filename': os.path.basename(file_path)
    })
    
    return HttpRequest('POST', url, data=file_chunk_generator(),
                      headers=headers, chunked=True, **kwargs).execute()

# ==================== RESTful快捷方法 ====================
def create_resource(url, data, **kwargs):
    """创建资源（POST别名）"""
    return post(url, data=data, **kwargs)

def update_resource(url, data, **kwargs):
    """完整更新资源（PUT别名）"""
    return put(url, data=data, **kwargs)

def partial_update(url, data, **kwargs):
    """部分更新资源（PATCH别名）"""
    return patch(url, data=data, **kwargs)

def fetch_resource(url, **kwargs):
    """获取资源（GET别名）"""
    return get(url, **kwargs)

def remove_resource(url, **kwargs):
    """删除资源（DELETE别名）"""
    return delete(url, **kwargs)

# ==================== 高级方法封装 ====================
def json_post(url, json_data, **kwargs):
    """发送JSON格式的POST请求"""
    headers = kwargs.get('headers', {})
    headers['Content-Type'] = 'application/json'
    return post(url, data=json.dumps(json_data), headers=headers, **kwargs)

def form_post(url, form_data, **kwargs):
    """发送表单格式的POST请求"""
    headers = kwargs.get('headers', {})
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return post(url, data=urlencode(form_data), headers=headers, **kwargs)

def upload_file(url, file_path, field_name='file', **kwargs):
    """上传文件便捷方法"""
    with open(file_path, 'rb') as f:
        files = {field_name: {
            'filename': os.path.basename(file_path),
            'content': f.read(),
            'content_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        }}
    return post(url, files=files, **kwargs)

# ==================== 特殊协议支持 ====================
def websocket(url, **kwargs):
    """WebSocket连接初始化（需配合其他库使用）"""
    headers = kwargs.get('headers', {})
    headers.update({
        'Connection': 'Upgrade',
        'Upgrade': 'websocket',
        'Sec-WebSocket-Version': '13',
        'Sec-WebSocket-Key': base64.b64encode(os.urandom(16)).decode()
    })
    return HttpRequest('GET', url, headers=headers, **kwargs)

def http2_prior_knowledge(url, **kwargs):
    """HTTP/2预先知识连接"""
    kwargs.setdefault('headers', {}).update({
        'Connection': 'Upgrade, HTTP2-Settings',
        'Upgrade': 'h2c',
        'HTTP2-Settings': '<base64url encoding of HTTP/2 SETTINGS payload>'
    })
    return HttpRequest('GET', url, **kwargs)

POST = post
GET = get
PUT = put
DELETE = delete
PATCH = patch
HEAD = head
OPTIONS = options
TRACE = trace
CONNECT = connect

if __name__ == '__main__':
    response = get('https://www.iana.org/help/example-domains', timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Content: {response.text}")