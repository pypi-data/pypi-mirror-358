import sys
from functools import wraps
import _collections_abc

# --------------- 基本类型定义 ---------------
def _cell_factory():
    a = 1
    def f():
        nonlocal a
    return f.__closure__[0]

# 定义所有类型对象
def _init_types():
    global FunctionType, LambdaType, CodeType, MappingProxyType, SimpleNamespace
    global CellType, GeneratorType, CoroutineType, AsyncGeneratorType
    global MethodType, BuiltinFunctionType, BuiltinMethodType
    global WrapperDescriptorType, MethodWrapperType, MethodDescriptorType
    global ClassMethodDescriptorType, ModuleType, TracebackType, FrameType
    global GetSetDescriptorType, MemberDescriptorType, DynamicClassAttribute
    global GeneratorWrapper, coroutine, GenericAlias, UnionType
    global EllipsisType, NoneType, NotImplementedType, __all__

    # 基础可调用对象类型
    def _f(): pass
    FunctionType = type(_f)
    LambdaType = type(lambda: None)  # 与 FunctionType 相同
    CodeType = type(_f.__code__)
    MappingProxyType = type(type.__dict__)
    SimpleNamespace = type(sys.implementation)

    # 闭包相关
    CellType = type(_cell_factory())

    # 生成器与协程
    def _g(): yield 1
    GeneratorType = type(_g())

    async def _c(): pass
    _c_obj = _c()
    CoroutineType = type(_c_obj)
    _c_obj.close()  # 避免 ResourceWarning

    async def _ag(): yield
    AsyncGeneratorType = type(_ag())

    # 方法与描述符
    class _C:
        def _m(self): pass
    MethodType = type(_C()._m)
    BuiltinFunctionType = type(len)
    BuiltinMethodType = type([].append)
    WrapperDescriptorType = type(object.__init__)
    MethodWrapperType = type(object().__str__)
    MethodDescriptorType = type(str.join)
    ClassMethodDescriptorType = type(dict.__dict__['fromkeys'])

    # 模块与异常跟踪
    ModuleType = type(sys)
    try:
        raise TypeError
    except TypeError as exc:
        TracebackType = type(exc.__traceback__)
        FrameType = type(exc.__traceback__.tb_frame)

    # 描述符类型
    GetSetDescriptorType = type(FunctionType.__code__)
    MemberDescriptorType = type(FunctionType.__globals__)

    # 特殊类型
    EllipsisType = type(Ellipsis)
    NoneType = type(None)
    NotImplementedType = type(NotImplemented)
    GenericAlias = type(list[int])
    UnionType = type(int | str)

# 初始化类型
_init_types()

# --------------- 动态类创建支持 ---------------
def new_class(name, bases=(), kwds=None, exec_body=None):
    resolved_bases = resolve_bases(bases)
    meta, ns, kwds = prepare_class(name, resolved_bases, kwds)
    if exec_body is not None:
        exec_body(ns)
    if resolved_bases is not bases:
        ns['__orig_bases__'] = bases
    return meta(name, resolved_bases, ns, **kwds)

def resolve_bases(bases):
    new_bases = list(bases)
    updated = False
    shift = 0
    for i, base in enumerate(bases):
        if isinstance(base, type):
            continue
        if not hasattr(base, "__mro_entries__"):
            continue
        new_base = base.__mro_entries__(bases)
        updated = True
        if not isinstance(new_base, tuple):
            raise TypeError("__mro_entries__ must return a tuple")
        else:
            new_bases[i+shift:i+shift+1] = new_base
            shift += len(new_base) - 1
    if not updated:
        return bases
    return tuple(new_bases)

def prepare_class(name, bases=(), kwds=None):
    if kwds is None:
        kwds = {}
    else:
        kwds = dict(kwds)
    if 'metaclass' in kwds:
        meta = kwds.pop('metaclass')
    else:
        if bases:
            meta = type(bases[0])
        else:
            meta = type
    if isinstance(meta, type):
        meta = _calculate_meta(meta, bases)
    if hasattr(meta, '__prepare__'):
        ns = meta.__prepare__(name, bases, **kwds)
    else:
        ns = {}
    return meta, ns, kwds

def _calculate_meta(meta, bases):
    winner = meta
    for base in bases:
        base_meta = type(base)
        if issubclass(winner, base_meta):
            continue
        if issubclass(base_meta, winner):
            winner = base_meta
            continue
        # else:
        raise TypeError("metaclass conflict: "
                        "the metaclass of a derived class "
                        "must be a (non-strict) subclass "
                        "of the metaclasses of all its bases")
    return winner


def get_original_bases(cls, /):
    try:
        return cls.__dict__.get("__orig_bases__", cls.__bases__)
    except AttributeError:
        raise TypeError(
            f"Expected an instance of type, not {type(cls).__name__!r}"
        ) from None


class DynamicClassAttribute:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        # next two lines make DynamicClassAttribute act the same as property
        self.__doc__ = doc or fget.__doc__
        self.overwrite_doc = doc is None
        # support for abstract methods
        self.__isabstractmethod__ = bool(getattr(fget, '__isabstractmethod__', False))

    def __get__(self, instance, ownerclass=None):
        if instance is None:
            if self.__isabstractmethod__:
                return self
            raise AttributeError()
        elif self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget):
        fdoc = fget.__doc__ if self.overwrite_doc else None
        result = type(self)(fget, self.fset, self.fdel, fdoc or self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result

    def setter(self, fset):
        result = type(self)(self.fget, fset, self.fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result

    def deleter(self, fdel):
        result = type(self)(self.fget, self.fset, fdel, self.__doc__)
        result.overwrite_doc = self.overwrite_doc
        return result


class _GeneratorWrapper:
    def __init__(self, gen):
        self.__wrapped = gen
        self.__isgen = gen.__class__ is GeneratorType
        self.__name__ = getattr(gen, '__name__', None)
        self.__qualname__ = getattr(gen, '__qualname__', None)
    def send(self, val):
        return self.__wrapped.send(val)
    def throw(self, tp, *rest):
        return self.__wrapped.throw(tp, *rest)
    def close(self):
        return self.__wrapped.close()
    @property
    def gi_code(self):
        return self.__wrapped.gi_code
    @property
    def gi_frame(self):
        return self.__wrapped.gi_frame
    @property
    def gi_running(self):
        return self.__wrapped.gi_running
    @property
    def gi_yieldfrom(self):
        return self.__wrapped.gi_yieldfrom
    cr_code = gi_code
    cr_frame = gi_frame
    cr_running = gi_running
    cr_await = gi_yieldfrom
    def __next__(self):
        return next(self.__wrapped)
    def __iter__(self):
        if self.__isgen:
            return self.__wrapped
        return self
    __await__ = __iter__

def coroutine(func):
    if not callable(func):
        raise TypeError('types.coroutine() expects a callable')

    if (func.__class__ is FunctionType and
        getattr(func, '__code__', None).__class__ is CodeType):

        co_flags = func.__code__.co_flags

        if co_flags & 0x180:
            return func

        if co_flags & 0x20:
            co = func.__code__
            func.__code__ = co.replace(co_flags=co.co_flags | 0x100)
            return func

    import functools
    import _collections_abc
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        coro = func(*args, **kwargs)
        if (coro.__class__ is CoroutineType or
            coro.__class__ is GeneratorType and coro.gi_code.co_flags & 0x100):
            return coro
        if (isinstance(coro, _collections_abc.Generator) and
            not isinstance(coro, _collections_abc.Coroutine)):
            return _GeneratorWrapper(coro)
        return coro

    return wrapped

GenericAlias = type(list[int])
UnionType = type(int | str)

EllipsisType = type(Ellipsis)
NoneType = type(None)
NotImplementedType = type(NotImplemented)

def __getattr__(name):
    if name == 'CapsuleType':
        import _socket
        return type(_socket.CAPI)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# --------------- 清理和导出 ---------------
__all__ = [n for n in globals() if n[:1] != '_']
__all__ += ['CapsuleType']

del sys, _collections_abc