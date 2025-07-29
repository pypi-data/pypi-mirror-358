"""
HTTP 响应处理模块
版本: 1.1.0
功能: 流式处理、内容解码、错误处理、链接解析等
"""

import io
import gzip
import zlib
import json
import chardet
import warnings
import datetime
from http.client import HTTPResponse
from urllib.parse import urlparse
from email.message import Message
from email.parser import BytesParser
from collections import OrderedDict

# ==================== 国际化支持 ====================
RESPONSE_TRANSLATIONS = {
    'en_US': {
        'json_decode_error': 'JSON decode error: {reason}',
        'content_encoding_error': 'Failed to decode content with {encoding} encoding',
        'stream_consumed': 'Stream content already consumed',
        'invalid_redirect': 'Invalid redirect location: {location}',
        'charset_detection_failed': 'Failed to detect charset, using fallback encoding'
    },
    'zh_CN': {
        'json_decode_error': 'JSON解码错误: {reason}',
        'content_encoding_error': '使用{encoding}编码解码内容失败',
        'stream_consumed': '流内容已被消费',
        'invalid_redirect': '无效的重定向地址: {location}',
        'charset_detection_failed': '字符集检测失败，使用备用编码'
    }
}

class I18nResponse:
    def __init__(self, locale='en_US'):
        self.locale = locale
        self._strings = RESPONSE_TRANSLATIONS.get(locale, RESPONSE_TRANSLATIONS['en_US'])
    
    def gettext(self, key, **kwargs):
        return self._strings.get(key, key).format(**kwargs)

# ==================== 异常定义 ====================
class ResponseError(Exception):
    """响应处理基础异常"""

class JSONDecodeError(ResponseError):
    """JSON解码异常"""

class StreamConsumedError(ResponseError):
    """流内容已消费异常"""

class ContentDecodeError(ResponseError):
    """内容解码异常"""

# ==================== 核心响应类 ====================
class HttpResponse:
    """增强型HTTP响应处理器"""
    
    def __init__(self, request, raw_response, elapsed=None, i18n=None):
        # 基础属性
        if not hasattr(raw_response, 'read'):
            raise TypeError("原始响应必须实现 read() 方法")
        self.request = request          # 关联的请求对象
        self.raw = raw_response         # 原始响应对象
        self.status_code = int(raw_response.status)
        self.reason = raw_response.reason
        self.elapsed = elapsed or datetime.timedelta(0)
        self.history = []               # 重定向历史记录
        
        # 国际化支持
        self.i18n = i18n or I18nResponse()
        
        # 头信息处理
        self.headers = CaseInsensitiveDict()
        self._parse_headers(raw_response.msg)
        
        # 内容处理相关
        self._content = None
        self._text = None
        self._json = None
        self._content_consumed = False
        self._stream = False
        
        # 编码信息
        self.encoding = self._detect_encoding()
        
        # 链接解析
        self.links = self._parse_links()
        
        # Cookie存储
        self.cookies = self._parse_cookies()
        
        # 缓存控制
        self._cache_info = self._parse_cache_control()
        
        # 性能指标
        self.metrics = {
            'dns_lookup': None,
            'tcp_handshake': None,
            'ssl_handshake': None,
            'ttfb': None,
            'download_time': None
        }
    
    def _parse_headers(self, message):
        """解析头信息"""
        if isinstance(message, Message):
            for name, value in message.items():
                self.headers[name] = value
        elif isinstance(message, list):
            for name, value in message:
                self.headers[name] = value
    
    def _detect_encoding(self):
        """检测内容编码"""
        # 1. 检查头信息中的编码声明
        content_type = self.headers.get('Content-Type', '')
        if 'charset=' in content_type:
            return content_type.split('charset=')[1].split(';')[0].strip()
        
        # 2. 检测内容编码
        if self.content:
            detected = chardet.detect(self.content)
            if detected['confidence'] > 0.9:
                return detected['encoding']
        
        # 3. 使用默认编码
        warnings.warn(self.i18n.gettext('charset_detection_failed'))
        return 'utf-8'
    
    @property
    def content(self):
        """原始字节内容"""
        if self._content is None and not self._content_consumed:
            self._content = self._read_raw_content()
            self._decode_content()
        return self._content
    
    @property
    def text(self):
        """解码后的文本内容"""
        if self._text is None:
            if self.content is None:
                return None
            try:
                self._text = str(self.content, self.encoding)
            except UnicodeDecodeError:
                self._text = self.content.decode(self.encoding, 'replace')
        return self._text
    
    @property
    def json(self):
        """JSON解码内容"""
        if self._json is None:
            try:
                self._json = json.loads(self.text)
            except json.JSONDecodeError as e:
                raise JSONDecodeError(
                    self.i18n.gettext('json_decode_error', reason=str(e))
                )
        return self._json
    
    def _read_raw_content(self):
        """安全读取原始内容"""
        try:
            content = self.raw.read()
        except AttributeError:
            raise RuntimeError("原始响应对象缺少 read() 方法")
        except (zlib.error, IOError) as e:
            raise ContentDecodeError(...) from e
        finally:
            # 安全关闭（如果对象支持）
            if hasattr(self.raw, 'close'):
                self.raw.close()
        return content
    
    def _decode_content(self):
        """处理内容编码"""
        encoding = self.headers.get('Content-Encoding', '').lower()
        if encoding == 'gzip':
            self._content = self._decompress_gzip()
        elif encoding == 'deflate':
            self._content = self._decompress_deflate()
        elif encoding == 'br':
            self._content = self._decompress_brotli()
    
    def _decompress_gzip(self):
        """解压GZIP内容"""
        try:
            return gzip.decompress(self._content)
        except OSError as e:
            raise ContentDecodeError(
                self.i18n.gettext('content_encoding_error', encoding='gzip')
            ) from e
    
    def _decompress_deflate(self):
        """解压DEFLATE内容"""
        try:
            return zlib.decompress(self._content)
        except zlib.error:
            # 尝试兼容不正确的zlib头
            return zlib.decompress(self._content, -zlib.MAX_WBITS)
    
    def _decompress_brotli(self):
        """解压Brotli内容（需要额外库）"""
        try:
            import brotli
            return brotli.decompress(self._content)
        except ImportError:
            raise RuntimeError("需要安装 brotli 库")
        except Exception as e:
            raise ContentDecodeError(
                self.i18n.gettext('content_encoding_error', encoding='br')
            ) from e
    
    def iter_content(self, chunk_size=1024, decode_unicode=False):
        """流式内容迭代器"""
        if self._content_consumed:
            raise StreamConsumedError(self.i18n.gettext('stream_consumed'))
        
        def generate():
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                if decode_unicode:
                    yield chunk.decode(self.encoding)
                else:
                    yield chunk
            self._content_consumed = True
        
        return generate()
    
    def _parse_links(self):
        """解析Link头信息"""
        links = {}
        link_header = self.headers.get('Link', '')
        if link_header:
            for link in link_header.split(', '):
                parts = link.split('; ')
                url = parts[0][1:-1]  # 去掉尖括号
                params = {}
                for part in parts[1:]:
                    key, value = part.split('=', 1)
                    params[key] = value.strip('"')
                links[params.get('rel')] = url
        return links
    
    def _parse_cookies(self):
        """解析Set-Cookie头信息"""
        from http.cookies import SimpleCookie
        
        cookies = SimpleCookie()
        for cookie in self.headers.get_list('Set-Cookie'):
            cookies.load(cookie)
        return {k: v.value for k, v in cookies.items()}
    
    def _parse_cache_control(self):
        """解析Cache-Control头信息"""
        cache_control = {}
        cc_header = self.headers.get('Cache-Control', '')
        for part in cc_header.split(','):
            part = part.strip()
            if '=' in part:
                key, value = part.split('=', 1)
                cache_control[key] = value
            else:
                cache_control[part] = True
        return cache_control
    
    def raise_for_status(self):
        """根据状态码抛出异常"""
        if 400 <= self.status_code < 500:
            raise ResponseError(
                f"{self.status_code} Client Error: {self.reason} for url: {self.request.url}"
            )
        elif 500 <= self.status_code < 600:
            raise ResponseError(
                f"{self.status_code} Server Error: {self.reason} for url: {self.request.url}"
            )
    
    @property
    def is_redirect(self):
        """是否是重定向响应"""
        return self.status_code in (301, 302, 303, 307, 308)
    
    @property
    def next(self):
        """获取重定向请求对象"""
        if not self.is_redirect:
            return None
        
        location = self.headers.get('Location')
        if not location:
            return None
        
        # 解析绝对URL
        next_url = urlparse(location)
        if not next_url.netloc:
            base_url = urlparse(self.request.url)
            next_url = base_url._replace(path=location).geturl()
        
        return self.request.copy(url=next_url)
    
    def __repr__(self):
        return f"<HttpResponse [{self.status_code}]>"

# ==================== 增强的字典类 ====================
class CaseInsensitiveDict:
    """支持多值的、大小写不敏感的字典"""
    def __init__(self):
        self._data = {}

    def __setitem__(self, key, value):
        lower_key = key.lower()
        if lower_key in self._data:
            self._data[lower_key][1].append(value)
        else:
            self._data[lower_key] = (key, [value])

    def get_list(self, key, default=None):
        lower_key = key.lower()
        return self._data.get(lower_key, (None, default or []))[1]

    def get(self, key, default=None):
        values = self.get_list(key)
        return values[0] if values else default

    def __getitem__(self, key):
        values = self.get_list(key)
        if not values:
            raise KeyError(key)
        return values[0]

    def __contains__(self, key):
        return key.lower() in self._data

    def keys(self):
        return [v[0] for v in self._data.values()]

    def items(self):
        return [(k, v) for k, values in self._data.values() for v in values]

# ==================== 修改后的头部解析 ====================
def _parse_headers(self, message):
    self.headers = CaseInsensitiveDict()
    if isinstance(message, Message):
        for name, value in message.items():
            self.headers[name] = value
    elif isinstance(message, list):
        for name, value in message:
            self.headers[name] = value

# ==================== 修复后的Cookie解析 ====================
def _parse_cookies(self):
    from http.cookies import SimpleCookie
    
    cookies = SimpleCookie()
    for cookie_str in self.headers.get_list('Set-Cookie', []):
        cookies.load(cookie_str)
    return {k: v.value for k, v in cookies.items()}

# ==================== 流式响应类 ====================
class StreamingHttpResponse(HttpResponse):
    """流式响应处理器"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stream = True
    
    @property
    def content(self):
        raise StreamConsumedError(self.i18n.gettext('stream_consumed'))
    
    @property
    def text(self):
        raise StreamConsumedError(self.i18n.gettext('stream_consumed'))
    
    def iter_lines(self, chunk_size=512, delimiter='\n'):
        """按行迭代内容"""
        pending = None
        for chunk in self.iter_content(chunk_size):
            if pending is not None:
                chunk = pending + chunk
            
            lines = chunk.split(delimiter)
            if lines[-1] != delimiter:
                pending = lines[-1]
                lines = lines[:-1]
            else:
                pending = None
            
            for line in lines:
                yield line
        
        if pending is not None:
            yield pending
    
    def save_to_file(self, file_path, chunk_size=1024*1024):
        """流式保存到文件"""
        with open(file_path, 'wb') as f:
            for chunk in self.iter_content(chunk_size):
                f.write(chunk)

# ==================== 示例用法 ====================
if __name__ == '__main__':
    # 模拟响应对象
    class MockResponse:
        status = 200
        reason = 'OK'
        msg = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Encoding', 'gzip'),
            ('Set-Cookie', 'session=abc123; Path=/')
        ]
        def read(self):
            return gzip.compress(b'<html>Hello World</html>')
        
        def close(self):  # 新增close方法
            self._closed = True
    
    request = type('FakeRequest', (), {'url': 'http://example.com'})()
    raw_resp = MockResponse()
    
    # 处理响应
    response = HttpResponse(request, raw_resp)
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Text: {response.text[:50]}")
    print(f"Cookies: {response.cookies}")