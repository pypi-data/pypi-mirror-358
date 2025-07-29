import ctypes, sys, subprocess

class AdminPrivilegeChecker:
    """Classes that automatically elevate privileges (Windows only)"""
    def __init__(self):
        self._restart_with_admin()

    def _restart_with_admin(self):
        if not self.__is_admin__():
            print()
            params = ' '.join([f'"{x}"' if ' ' in x else x for x in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params,
                None,
                1
            )
            sys.exit()

    def __is_admin__(self):
        """检查当前是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def admin(self):
        """
        If you don't have admin privileges, the function will return False, if you have admin privileges,
        The function will return True.
        """
        if not self.__is_admin__():
            ctypes.windll.user32.MessageBoxW(0, "There are still no administrator privileges.", "Error.", 0x10)
            #print("There are still no administrator privileges.")
            return False

        else:
            return True
        
import mpmath

 
def pi(numbers):
    mpmath.mp.dps = numbers
    return mpmath.pi

 
def factorial(n):
    """计算阶乘"""
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

 
def sin(x, num_terms=10):
    """使用泰勒级数展开计算正弦函数"""
    result = 0
    for n in range(num_terms):
        term = ((-1) ** n) * (x ** (2 * n + 1)) / factorial(2 * n + 1)
        result += term
    return result

 
def cos(x, num_terms=10):
    """使用泰勒级数展开计算余弦函数"""
    result = 0
    for n in range(num_terms):
        term = ((-1) ** n) * (x ** (2 * n)) / factorial(2 * n)
        result += term
    return result

 
def tan(x, num_terms=10):
    """计算正切函数"""
    cos_value = cos(x, num_terms)
    if cos_value == 0:
        return float('inf')  # 当 cos 为 0 时，tan 为无穷大
    return sin(x, num_terms) / cos_value

 
def cot(x, num_terms=10):
    """计算余切函数"""
    tan_value = tan(x, num_terms)
    if tan_value == 0:
        return float('inf')  # 当 tan 为 0 时，cot 为无穷大
    return 1 / tan_value

class ComplexNumber:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def __add__(self, other):
        return ComplexNumber(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other):
        return ComplexNumber(self.real - other.real, self.imag - other.imag)

    def __mul__(self, other):
        real_part = self.real * other.real - self.imag * other.imag
        imag_part = self.real * other.imag + self.imag * other.real
        return ComplexNumber(real_part, imag_part)

    def __truediv__(self, other):
        denominator = other.real ** 2 + other.imag ** 2
        real_part = (self.real * other.real + self.imag * other.imag) / denominator
        imag_part = (self.imag * other.real - self.real * other.imag) / denominator
        return ComplexNumber(real_part, imag_part)

     
    def __str__(self):
        return f"{self.real} + {self.imag}i"
    
 
def sqrt(a, tolerance=1e-6, max_iterations=100):
    x = a  # 初始猜测值
    for _ in range(max_iterations):
        f = x ** 2 - a
        f_prime = 2 * x
        delta_x = f / f_prime
        x -= delta_x
        if abs(delta_x) < tolerance:
            break
    return x

 
def exp(x, num_terms=10):
    result = 0
    for n in range(num_terms):
        term = (x ** n) / factorial(n)
        result += term
    return result

 
def ln(x, tolerance=1e-6, max_iterations=100):
    if x <= 0:
        raise ValueError("Input must be positive")
    
    y = 1.0  # 双精度提升精度
    for _ in range(max_iterations):
        try:
            ey = exp(y)
        except OverflowError:
            y = "inf"  # 溢出时返回无穷大
            break
        
        delta = (ey - x) / ey
        y -= delta
        if abs(delta) < tolerance:
            break
    else:  # 未收敛处理
        raise Exception(f"Failed to converge in {max_iterations} iterations")
    
    return y

 
def power(x, n):
    result = 1
    if n >= 0:
        for _ in range(n):
            result *= x
    else:
        for _ in range(-n):
            result /= x
    return result

import math

 
def combination(n, k):
    if k > n or k < 0:
        return 0
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

 
def log10(x, tolerance=1e-6, max_iterations=100):
    """
    计算以 10 为底的对数 log10(x)
    :param x: 输入值
    :param tolerance: 收敛的容差
    :param max_iterations: 最大迭代次数
    :return: log10(x) 的近似值
    """
    ln_10 = ln(10, tolerance, max_iterations)
    return ln(x, tolerance, max_iterations) / ln_10

 
def sinh(x, num_terms=10):
    """
    计算双曲正弦函数 sinh(x) 的近似值
    :param x: 输入值
    :param num_terms: 计算指数函数时泰勒级数展开的项数
    :return: sinh(x) 的近似值
    """
    return (exp(x, num_terms) - exp(-x, num_terms)) / 2

 
def cosh(x, num_terms=10):
    """
    计算双曲余弦函数 cosh(x) 的近似值
    :param x: 输入值
    :param num_terms: 计算指数函数时泰勒级数展开的项数
    :return: cosh(x) 的近似值
    """
    return (exp(x, num_terms) + exp(-x, num_terms)) / 2

 
def tanh(x, num_terms=10):
    """
    计算双曲正切函数 tanh(x) 的近似值
    :param x: 输入值
    :param num_terms: 计算指数函数时泰勒级数展开的项数
    :return: tanh(x) 的近似值
    """
    sinh_val = sinh(x, num_terms)
    cosh_val = cosh(x, num_terms)
    return sinh_val / cosh_val

 
def floor(x):
    return int(x) if x >= 0 else int(x) - 1

 
def absolute_value(x):
    return x if x >= 0 else -x

 
def combination(n, k):
    if k > n or k < 0:
        return 0
    return factorial(n) // (factorial(k) * factorial(n - k))

import hashlib

def __calculate_hash__(data, algorithm):
    if isinstance(data, str):
        data = data.encode('utf-8')
    hash_object = algorithm(data)
    hex_dig = hash_object.hexdigest()
    return hex_dig

def sha256(data):
    return __calculate_hash__(data, hashlib.sha256)

def sha384(data):
    return __calculate_hash__(data, hashlib.sha384)

def sha224(data):
    return __calculate_hash__(data, hashlib.sha224)

def sha1(data):
    return __calculate_hash__(data, hashlib.sha1)

def sha512(data):
    return __calculate_hash__(data, hashlib.sha512)

def md5(data):
    return __calculate_hash__(data, hashlib.md5)

def blake2b(data):
    return __calculate_hash__(data, hashlib.blake2b)

def sha3_256(data):
    return __calculate_hash__(data, hashlib.sha3_256)

def shake_128(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    hash_object = hashlib.shake_128(data)
    hex_dig = hash_object.hexdigest(16)
    return hex_dig

def shake_256(data):
    return __calculate_hash__(data, hashlib.shake_256)

def sha3_384(data):
    return __calculate_hash__(data, hashlib.sha3_384)

def sha3_512(data):
    return __calculate_hash__(data, hashlib.sha3_512)

def blake2s(data):
    return __calculate_hash__(data, hashlib.blake2s)

def cmd(command):
    process = subprocess.Popen(command, shell=True)
    process.wait()
    return process.returncode

def powershell(command, capture_output=True, timeout=None):
    """
    A Python function that executes a command in PowerShell.
    Parameter:
        command: PowerShell command to execute (string)
        capture_output: Whether to capture the output (default True)
        timeout: timeout period (seconds, unlimited by default)
    Return:
        A CompletedProcess object that contains the execution result.
    """
    args = [
        "powershell.exe" if sys.platform == "win32" else "pwsh",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        f"& {{{command}}}"
    ]
    
    result = subprocess.run(
        args,
        text=True,
        capture_output=capture_output,
        shell=False,
        timeout=timeout,
        encoding="utf-8",
        errors="replace"
    )
    
    return result

import math
from numbers import Real

class HF(float):
    """
    Customize floating-point types, inherit native floats, and extend functionality
    Features include:
    - Carry metadata (e.g. units)
    - Automatically hold the calculated type
    - Unit consistency checks
    - Base Unit Conversion
    """
    
    # 单位换算表 (from_unit, to_unit): rate
    CONVERSION_TABLE = {
        ('m', 'km'): 0.001,
        ('kg', 'g'): 1000,
        ('s', 'min'): 1/60
    }

    def __new__(cls, value, unit=None, min_val=-math.inf, max_val=math.inf):
        # 值域校验
        if not (min_val <= float(value) <= max_val):
            raise ValueError(f"Value must be in [{min_val}, {max_val}]")
        
        # 创建不可变对象
        instance = super().__new__(cls, value)
        instance.unit = unit
        instance.min_val = min_val
        instance.max_val = max_val
        return instance

    def __repr__(self):
        return f"HF({super().__repr__()}, unit='{self.unit}')"

    def __str__(self):
        return f"{super().__str__()} {self.unit}" if self.unit else super().__str__()

    def _wrap_result(self, result):
        """包装运算结果为HF实例"""
        if isinstance(result, Real):
            return HF(
                result,
                unit=self.unit,
                min_val=self.min_val,
                max_val=self.max_val
            )
        return result

    # 运算符重载
    def __add__(self, other):
        other_val = other if isinstance(other, Real) else float(other)
        return self._wrap_result(super().__add__(other_val))
    
    def __sub__(self, other):
        other_val = other if isinstance(other, Real) else float(other)
        return self._wrap_result(super().__sub__(other_val))
    
    def __mul__(self, other):
        other_val = other if isinstance(other, Real) else float(other)
        return self._wrap_result(super().__mul__(other_val))
    
    def __truediv__(self, other):
        other_val = other if isinstance(other, Real) else float(other)
        return self._wrap_result(super().__truediv__(other_val))
    
    # 反向运算符
    __radd__ = __add__
    __rmul__ = __mul__
    
    def __rsub__(self, other):
        return self._wrap_result(float(other) - float(self))
    
    def __rtruediv__(self, other):
        return self._wrap_result(float(other) / float(self))

    # 比较运算符
    def __eq__(self, other):
        if isinstance(other, HF):
            return super().__eq__(other) and self.unit == other.unit
        return super().__eq__(other)
    
    # 单位转换
    def convert(self, target_unit):
        """基于预设换算表进行单位转换"""
        for (from_unit, to_unit), rate in self.CONVERSION_TABLE.items():
            if self.unit == from_unit and target_unit == to_unit:
                return HF(
                    self * rate,
                    unit=target_unit,
                    min_val=self.min_val,
                    max_val=self.max_val
                )
            elif self.unit == to_unit and target_unit == from_unit:
                return HF(
                    self / rate,
                    unit=target_unit,
                    min_val=self.min_val,
                    max_val=self.max_val
                )
        raise ValueError(f"Unsupported conversion: {self.unit} to {target_unit}")

    # 值域检查装饰器
    def _check_bounds(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if hasattr(result, 'min_val'):
                if not (result.min_val <= float(result) <= result.max_val):
                    raise ValueError("Result out of bounds")
            return result
        return wrapper

    # 应用装饰器到关键方法
    __add__ = _check_bounds(__add__)
    __sub__ = _check_bounds(__sub__)
    __mul__ = _check_bounds(__mul__)
    __truediv__ = _check_bounds(__truediv__)

Real.register(HF)

from types import FunctionType
from functools import wraps

class WithHtyy:
    """Make decorated functions/classes automatically support with statements."""
    def __init__(self, target):
        self.target = target  # 保存被装饰的原始对象

    def _handle_function(self):
        """处理函数装饰逻辑"""
        @wraps(self.target)
        def wrapper(*args, **kwargs):
            # 返回一个上下文管理器实例
            return self.ContextWrapper(self.target, args, kwargs)
        return wrapper

    def _handle_class(self):
        """处理类装饰逻辑"""
        orig_init = self.target.__init__

        # 动态添加上下文管理方法
        def new_init(self_, *args, **kwargs):
            orig_init(self_, *args, **kwargs)
            # 绑定原始对象的上下文方法
            self_._htyy_enter = getattr(self_, "__enter__", None)
            self_._htyy_exit = getattr(self_, "__exit__", None)

        # 添加标准上下文协议方法
        def __enter__(self_):
            if self_._htyy_enter:
                return self_._htyy_enter()
            return self_

        def __exit__(self_, exc_type, exc_val, exc_tb):
            if self_._htyy_exit:
                return self_._htyy_exit(exc_type, exc_val, exc_tb)
            # 默认自动调用close方法（如果存在）
            if hasattr(self_, "close"):
                self_.close()

        self.target.__init__ = new_init
        self.target.__enter__ = __enter__
        self.target.__exit__ = __exit__
        return self.target

    def __call__(self, *args, **kwargs):
        # 根据被装饰对象的类型分发处理
        if isinstance(self.target, FunctionType):
            return self._handle_function()(*args, **kwargs)
        else:
            return self._handle_class()(*args, **kwargs)

    class ContextWrapper:
        """Context Manager wrapper dedicated to function decorators."""
        def __init__(self, func, args, kwargs):
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.resource = None

        def __enter__(self):
            self.resource = self.func(*self.args, **self.kwargs)
            return self.resource

        def __exit__(self, exc_type, exc_val, exc_tb):
            # 自动清理资源（如果对象有close方法）
            if hasattr(self.resource, "close"):
                self.resource.close()
            elif hasattr(self.func, "htyy_cleanup"):
                # 自定义清理函数
                self.func.htyy_cleanup(self.resource)

class HtyySet:
    """
    Custom collection types with support for metadata tagging and chaining operations
    Key features:
    - All collection operations return HtyySet instances
    - Support for labeling systems
    - Automatically maintain operational history
    """

    def __init__(self, iterable=(), tags=None, _history=None):
        self._data = set(iterable)
        self.tags = set(tags) if tags else set()
        # 操作历史记录（用于审计）
        self.history = _history if _history else []

    def _wrap_operation(self, result_set, operation, other=None):
        """包装集合操作结果"""
        new_history = self.history + [
            f"{operation}: {getattr(other, '_data', other)}"
        ]
        return HtyySet(
            result_set,
            tags=self.tags.copy(),
            _history=new_history
        )

    # 基本集合运算符重载
    def __or__(self, other):
        return self._wrap_operation(
            self._data | self._get_other_data(other),
            "union", other
        )

    def __and__(self, other):
        return self._wrap_operation(
            self._data & self._get_other_data(other),
            "intersection", other
        )

    def __sub__(self, other):
        return self._wrap_operation(
            self._data - self._get_other_data(other),
            "difference", other
        )

    def __xor__(self, other):
        return self._wrap_operation(
            self._data ^ self._get_other_data(other),
            "symmetric_difference", other
        )

    # 比较运算符
    def __le__(self, other):
        return self._data <= self._get_other_data(other)

    def __lt__(self, other):
        return self._data < self._get_other_data(other)

    def __ge__(self, other):
        return self._data >= self._get_other_data(other)

    def __gt__(self, other):
        return self._data > self._get_other_data(other)

    def __eq__(self, other):
        return self._data == self._get_other_data(other)

    # 集合方法扩展
    def add(self, element):
        """不可变添加（返回新实例）"""
        return self._wrap_operation(
            self._data | {element},
            "add", element
        )

    def remove(self, element):
        """不可变移除（返回新实例）"""
        if element not in self._data:
            raise KeyError(element)
        return self._wrap_operation(
            self._data - {element},
            "remove", element
        )

    # 标签管理系统
    def tag(self, *tags):
        """添加标签并返回新实例"""
        return HtyySet(
            self._data,
            tags=self.tags | set(tags),
            _history=self.history.copy()
        )

    def untag(self, tag):
        """移除标签并返回新实例"""
        return HtyySet(
            self._data,
            tags=self.tags - {tag},
            _history=self.history.copy()
        )

    # 辅助方法
    def _get_other_data(self, other):
        """获取其他对象的数据集"""
        if isinstance(other, HtyySet):
            return other._data
        try:
            return set(other)
        except TypeError:
            return {other}

    # 原生集合行为模拟
    def __contains__(self, element):
        return element in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        tag_info = f" tags={self.tags}" if self.tags else ""
        history_info = f" ({len(self.history)} ops)" if self.history else ""
        return f"HtyySet({self._data}{tag_info}{history_info})"

    # 高级功能
    def filter(self, condition):
        """Condition filtering and keep history."""
        return self._wrap_operation(
            {x for x in self._data if condition(x)},
            f"filter[{condition.__name__}]"
        )

    def map(self, transform):
        """element conversion and preservation of history."""
        return self._wrap_operation(
            {transform(x) for x in self._data},
            f"map[{transform.__name__}]"
        )

    def audit_log(self):
        """Get the ActionTrail logs."""
        return "\n".join(
            f"[{i+1}] {action}"
            for i, action in enumerate(self.history)
        )
    
class HtNone:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "None"

    def __bool__(self):
        return False
    
class HLen:
    def __init__(self, obj, min_len=None, max_len=None):
        self.length = len(obj)
        self._validate(self.length, min_len, max_len)
    
    def _validate(self, length, min_len, max_len):
        if min_len is not None and length < min_len:
            raise ValueError(f"Length {length} less than minimum {min_len}.")
        if max_len is not None and length > max_len:
            raise ValueError(f"The length {length} is greater than the maximum {max_len}.")
    
    def __repr__(self):
        return str(self.length)
    
@classmethod
def d(cls):
    return cls.getcwd(cls)