import itertools
import math
import random

__all__ = [
    "derivative",
    "integral_1d",
    "monte_carlo_1d",
    "gradient",
    "integral",
    "sparse_integral",
    "monte_carlo_integral",
    "sum_of_squares",
]


def _bounds(low, high):
    if isinstance(low, (int, float)) and isinstance(high, (int, float)):
        lows, highs = (float(low),), (float(high),)
    else:
        lows = tuple(float(v) for v in low)
        highs = tuple(float(v) for v in high)
    if len(lows) != len(highs) or not lows:
        raise ValueError("low 與 high 必須是同長且非空的序列")
    if any(a >= b for a, b in zip(lows, highs)):
        raise ValueError("必須滿足 low[i] < high[i]")
    return lows, highs


def _call(f, point):
    try:
        return f(point)
    except TypeError:
        if len(point) == 1:
            return f(point[0])
        raise


def _steps(steps, n):
    if isinstance(steps, int):
        result = (steps,) * n
    else:
        result = tuple(int(s) for s in steps)
    if len(result) != n or any(s < 1 for s in result):
        raise ValueError("steps 必須是正整數或長度為 n 的正整數序列")
    return result


def derivative(f, x, h=1e-5, method="central"):
    if method == "central":
        return (f(x + h) - f(x - h)) / (2 * h)
    if method == "forward":
        return (f(x + h) - f(x)) / h
    if method == "backward":
        return (f(x) - f(x - h)) / h
    raise ValueError("method 必須是 central、forward 或 backward")


def integral_1d(f, low, high, steps=1000, method="midpoint"):
    lo, hi = _bounds(low, high)
    lo, hi = lo[0], hi[0]
    steps = _steps(steps, 1)[0]
    h = (hi - lo) / steps
    fv = lambda t: _call(f, (t,))
    if method == "midpoint":
        return h * sum(fv(lo + (i + 0.5) * h) for i in range(steps))
    if method == "left":
        return h * sum(fv(lo + i * h) for i in range(steps))
    if method == "right":
        return h * sum(fv(lo + (i + 1) * h) for i in range(steps))
    if method == "trapezoid":
        return h * (0.5 * fv(lo) + sum(fv(lo + i * h) for i in range(1, steps)) + 0.5 * fv(hi))
    if method == "simpson":
        if steps % 2:
            raise ValueError("Simpson 法需要偶數個等分")
        odd = sum(fv(lo + i * h) for i in range(1, steps, 2))
        even = sum(fv(lo + i * h) for i in range(2, steps, 2))
        return h * (fv(lo) + 4 * odd + 2 * even + fv(hi)) / 3
    raise ValueError("method 必須是 midpoint、left、right、trapezoid 或 simpson")


def gradient(f, x, h=1e-5):
    x = tuple(float(v) for v in x)
    if not x:
        raise ValueError("x 不可為空")
    result = []
    for i in range(len(x)):
        plus, minus = list(x), list(x)
        plus[i] += h
        minus[i] -= h
        result.append((_call(f, tuple(plus)) - _call(f, tuple(minus))) / (2 * h))
    return tuple(result)


def _rule_1d(level, a, b):
    if level == 1:
        return (((a + b) / 2,), (b - a,))
    m = 2 ** (level - 1)
    h = (b - a) / m
    nodes = tuple(a + k * h for k in range(m + 1))
    weights = [h / 3] * (m + 1)
    for k in range(1, m):
        weights[k] = 4 * h / 3 if k % 2 else 2 * h / 3
    return nodes, tuple(weights)


def _compositions(total, n):
    if n == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _compositions(total - first, n - 1):
            yield (first,) + rest


def sparse_integral(f, low, high, level=1):
    lows, highs = _bounds(low, high)
    n = len(lows)
    if level < 1:
        raise ValueError("level 必須是大於等於 1 的整數")
    cache = {}
    total = 0.0
    for extra in range(level + 1):
        coef = (-1) ** (level - extra) * math.comb(n - 1, level - extra)
        if coef == 0:
            continue
        for exponents in _compositions(extra, n):
            pairs = []
            for j, exponent in enumerate(exponents):
                key = (j, exponent + 1)
                if key not in cache:
                    cache[key] = tuple(zip(*_rule_1d(exponent + 1, lows[j], highs[j])))
                pairs.append(cache[key])
            subtotal = 0.0
            for combo in itertools.product(*pairs):
                weight = 1.0
                for _, w in combo:
                    weight *= w
                subtotal += weight * _call(f, tuple(v for v, _ in combo))
            total += coef * subtotal
    return total


def integral(f, low, high, steps=10, method="auto", level=1, max_cells=2_000_000):
    lows, highs = _bounds(low, high)
    n = len(lows)
    steps = _steps(steps, n)
    cells = math.prod(steps)
    if method == "auto":
        method = "grid" if cells <= max_cells else "sparse"
    if method == "sparse":
        return sparse_integral(f, lows, highs, level)
    if method != "grid":
        raise ValueError("method 必須是 auto、grid 或 sparse")
    if cells > max_cells:
        raise ValueError(
            f"全網格需要 {cells} 個取樣點，超過上限 {max_cells}；"
            "請改用 method='sparse' 或 monte_carlo_integral"
        )
    widths = tuple((b - a) / s for a, b, s in zip(lows, highs, steps))
    volume = math.prod(b - a for a, b in zip(lows, highs))
    total = 0.0
    for index in itertools.product(*(range(s) for s in steps)):
        point = tuple(a + (i + 0.5) * w for a, i, w in zip(lows, index, widths))
        total += _call(f, point)
    return volume * total / cells


def monte_carlo_integral(f, low, high, samples=100_000, seed=0, with_error=False):
    lows, highs = _bounds(low, high)
    if samples < 1:
        raise ValueError("samples 必須大於等於 1")
    rng = random.Random(seed)
    volume = math.prod(b - a for a, b in zip(lows, highs))
    total = 0.0
    squares = 0.0
    for _ in range(samples):
        point = tuple(a + (b - a) * rng.random() for a, b in zip(lows, highs))
        value = _call(f, point)
        total += value
        squares += value * value
    mean = total / samples
    if not with_error:
        return volume * mean
    variance = max(0.0, squares / samples - mean * mean) * samples / (samples - 1) if samples > 1 else 0.0
    return volume * mean, volume * math.sqrt(variance / samples)


def monte_carlo_1d(f, low, high, samples=100_000, seed=0):
    return monte_carlo_integral(f, low, high, samples=samples, seed=seed)


def sum_of_squares(x):
    if isinstance(x, (int, float)):
        return float(x) * float(x)
    return sum(float(v) * float(v) for v in x)
