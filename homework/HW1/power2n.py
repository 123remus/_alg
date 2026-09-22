"""
HW1 : 用四種方法實作計算 2^n，並比較執行效率

方法 1   : 內建冪次運算  2**n
方法 2a  : 遞迴          power2n(n-1)+power2n(n-1)   (重複呼叫兩次)
方法 2b  : 遞迴          2*power2n(n-1)              (呼叫一次再乘 2)
方法 3   : 遞迴 + 查表   與 2a 同，但先查表再遞迴     (memoization)

測試 : n = 100，看哪個快、哪個慢、哪個根本算不出來。
"""

import signal
import time

N = 100          # 測試用的 n
TIMEOUT = 5      # 每個方法的最長等待秒數(超過視為「算不出來」)
SMALL_N = 20     # 用來驗證正確性與觀察成長的小 n


class TimeoutError(Exception):
    pass


def _handle_timeout(signum, frame):
    raise TimeoutError()


# ------------------------------------------------------------
# 方法 1 : 用內建運算子 (O(1) 大數運算，C 語言實作)
# ------------------------------------------------------------
def power2n_v1(n):
    return 2 ** n


# ------------------------------------------------------------
# 方法 2a : 遞迴，呼叫自己兩次 (O(2^n) 次呼叫，指數爆炸)
# ------------------------------------------------------------
def power2n_v2a(n):
    if n == 0:
        return 1
    return power2n_v2a(n - 1) + power2n_v2a(n - 1)


# ------------------------------------------------------------
# 方法 2b : 遞迴，呼叫自己一次再乘 2 (O(n) 次呼叫)
# ------------------------------------------------------------
def power2n_v2b(n):
    if n == 0:
        return 1
    return 2 * power2n_v2b(n - 1)


# ------------------------------------------------------------
# 方法 3 : 遞迴 + 查表 (memoization)
#          先查表，表裡沒有才遞迴，所以一樣只需算 n 次
# ------------------------------------------------------------
_table = {}


def power2n_v3(n):
    if n in _table:
        return _table[n]
    if n == 0:
        _table[0] = 1
        return 1
    _table[n] = power2n_v3(n - 1) + power2n_v3(n - 1)
    return _table[n]


# ------------------------------------------------------------
# 測試工具
# ------------------------------------------------------------
def run_with_timeout(func, n, timeout=TIMEOUT):
    """執行 func(n)，超過 timeout 秒就強制中止，避免等 2^n 年。"""
    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    start = time.perf_counter()
    try:
        result = func(n)
        elapsed = time.perf_counter() - start
        signal.setitimer(signal.ITIMER_REAL, 0)
        return result, elapsed, None
    except TimeoutError:
        elapsed = time.perf_counter() - start
        signal.setitimer(signal.ITIMER_REAL, 0)
        return None, elapsed, f"超過 {timeout} 秒沒算完，強制中止"


def check_correctness():
    """先用小 n 驗證四種方法結果都正確。"""
    print("=" * 60)
    print(f"正確性驗證 (n = {SMALL_N}, 期望值 = 2^{SMALL_N})")
    print("=" * 60)
    expected = 2 ** SMALL_N
    results = {
        "方法1 (2**n)                 ": power2n_v1(SMALL_N),
        "方法2a (遞迴+遞迴)           ": power2n_v2a(SMALL_N),
        "方法2b (遞迴*2)              ": power2n_v2b(SMALL_N),
        "方法3  (遞迴+查表)           ": power2n_v3(SMALL_N),
    }
    all_ok = True
    for name, val in results.items():
        ok = "OK" if val == expected else "FAIL"
        all_ok = all_ok and (val == expected)
        print(f"  {name} : {val == expected}")
    print(f"  全部正確 : {all_ok}\n")
    return all_ok


def growth_test_v2a():
    """觀察方法 2a 的執行時間如何隨 n 指數成長。"""
    print("=" * 60)
    print("方法2a 成長趨勢 (證明它會指數爆炸)")
    print("=" * 60)
    for n in (10, 15, 18, 20, 22):
        _, elapsed, _ = run_with_timeout(power2n_v2a, n, timeout=5)
        calls = 2 ** (n + 1) - 1  # 總共的遞迴呼叫次數
        print(f"  n={n:>3}  呼叫次數≈2^{n+1}≈{calls:>14,} 次  花費 {elapsed:.4f} 秒")
    print()


def compare_at_n100():
    """正式比較 n=100 時四種方法的效率。"""
    print("=" * 60)
    print(f"效率比較 (n = {N})")
    print("=" * 60)
    v3_table_backup = dict(_table)  # 清空查表，確保公平
    _table.clear()

    funcs = {
        "方法1 : 2**n": power2n_v1,
        "方法2a: 遞迴+遞迴     ": power2n_v2a,
        "方法2b: 2*遞迴        ": power2n_v2b,
        "方法3 : 遞迴+查表     ": power2n_v3,
    }

    for name, func in funcs.items():
        result, elapsed, err = run_with_timeout(func, N)
        if err is not None:
            print(f"  {name} : {err}")
        else:
            correct = (result == 2 ** N)
            print(f"  {name} : 花費 {elapsed:.6f} 秒  結果正確:{correct}\n       = {result}")

    _table.update(v3_table_backup)
    print()


if __name__ == "__main__":
    print(f"2^n 四種實作效率比較  (Python {'.'.join(map(str, __import__('sys').version_info[:3]))})")
    check_correctness()
    growth_test_v2a()
    compare_at_n100()