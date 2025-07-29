import math
import time

# 全局状态
_seed = int(time.time() * 1000) % 2147483647  # 初始种子

def seed(a=None):
    """设置全局种子"""
    global _seed
    if a is None:
        a = int(time.time() * 1000)
    _seed = a % 2147483647

def _next():
    """线性同余生成器（LCG）生成下一个整数"""
    global _seed
    _seed = (_seed * 1103515245 + 12345) % 2147483648
    return _seed

def random():
    """生成 [0.0, 1.0) 的浮点数"""
    return _next() / 2147483648.0

def expovariate(lambd):
    """指数分布随机数（lambda 必须 > 0）"""
    if lambd <= 0:
        raise ValueError("lambda must be > 0")
    return -math.log(1.0 - random()) / lambd  # 直接调用全局 random()

def gammavariate(alpha, beta):
    """Gamma 分布生成函数（支持任意 alpha > 0, beta > 0）"""
    if alpha <= 0 or beta <= 0:
        raise ValueError("alpha and beta must be > 0")
    
    # 分情况处理 alpha 的大小
    if alpha > 1.0:
        # Marsaglia 和 Tsang 的算法（适用于 alpha > 1）
        ainv = math.sqrt(2.0 * alpha - 1.0)
        bbb = alpha - math.log(4.0)
        ccc = alpha + ainv
        while True:
            u1 = random()
            if u1 <= 1e-7 or u1 >= 0.9999999:
                continue  # 避免极端值
            u2 = 1.0 - random()
            v = math.log(u1 / (1.0 - u1)) / ainv
            x = alpha * math.exp(v)
            z = u1 * u1 * u2
            r = bbb + ccc * v - x
            if r + (1.0 + math.log(4.5)) >= 4.5 * z or r >= math.log(z):
                return x * beta
    elif alpha == 1.0:
        # 退化为指数分布
        return -math.log(1.0 - random()) * beta
    else:
        # 阿尔法 < 1 的算法（Ahrens-Dieter）
        while True:
            u = random()
            b = (math.e + alpha) / math.e
            p = b * u
            if p <= 1.0:
                x = p ** (1.0 / alpha)
            else:
                x = -math.log((b - p) / alpha)
            u1 = random()
            if p > 1.0:
                if u1 <= x ** (alpha - 1.0):
                    break
            else:
                if u1 <= math.exp(-x):
                    break
        return x * beta

def betavariate(alpha, beta):
    """Beta 分布随机数（基于 Gamma 分布）"""
    y = gammavariate(alpha, 1.0)
    if y == 0:
        return 0.0
    else:
        return y / (y + gammavariate(beta, 1.0))
    
