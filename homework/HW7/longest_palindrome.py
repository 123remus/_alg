#!/usr/bin/env python3
"""HW7：最長回文子串 — 動態規劃 vs 非動態規劃（中心擴展 + Manacher）

同一個文字問題，用三種演算法求解：
  1. 動態規劃 (DP)          — O(n^2) 時間 / O(n^2) 空間
  2. 中心擴展 (非 DP)        — O(n^2) 時間 / O(1) 空間
  3. Manacher 演算法 (非 DP) — O(n)   時間 / O(n)   空間

三者互相驗證，並在隨機字串上實測耗時。
"""

import random
import string
import time

# ============================================================
# 方法一：動態規劃 (Dynamic Programming)
# ============================================================
# 狀態：dp[i][j] = s[i..j] 是否為回文
# 轉移：dp[i][j] = (s[i] == s[j]) and dp[i+1][j-1]
# 邊界：dp[i][i] = True（長度 1）
#       dp[i][i+1] = (s[i] == s[i+1])（長度 2）
# 填表順序：按「區間長度」由小到大，保證 dp[i+1][j-1] 已算好。

def longest_palindrome_dp(s: str) -> str:
    n = len(s)
    if n == 0:
        return ""
    dp = [[False] * n for _ in range(n)]
    start, max_len = 0, 1

    for i in range(n):
        dp[i][i] = True

    for i in range(n - 1):
        if s[i] == s[i + 1]:
            dp[i][i + 1] = True
            start, max_len = i, 2

    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and dp[i + 1][j - 1]:
                dp[i][j] = True
                if length > max_len:
                    start, max_len = i, length

    return s[start:start + max_len]


# ============================================================
# 方法二：中心擴展法 (Expand Around Center) — 非動態規劃
# ============================================================
# 回文必定「左右對稱於某個中心」，從中心向兩側擴展比對即可。
# 中心有 2n-1 個：n 個字元中心（奇數長度）+ n-1 個間隙中心（偶數長度）。

def longest_palindrome_expand(s: str) -> str:
    n = len(s)
    if n == 0:
        return ""
    start, max_len = 0, 1

    def expand(left: int, right: int) -> int:
        """從中心向兩側擴展，回傳可擴展的最大半徑。"""
        while left >= 0 and right < n and s[left] == s[right]:
            left -= 1
            right += 1
        return right - left - 1

    for i in range(n):
        len1 = expand(i, i)          # 奇數長度回文
        len2 = expand(i, i + 1)      # 偶數長度回文
        cur = max(len1, len2)
        if cur > max_len:
            max_len = cur
            start = i - (cur - 1) // 2

    return s[start:start + max_len]


# ============================================================
# 方法三：Manacher 演算法 — 非動態規劃，O(n)
# ============================================================
# 核心技巧：在字串中插入分隔符（如 '#'），把奇/偶長度回文統一成奇數長度，
# 再利用「回文鏡像」性質，讓每個中心的擴展結果能重用先前算過的資訊。
# p[i] = 以 t[i] 為中心的最長回文半徑（含中心本身）。

def longest_palindrome_manacher(s: str) -> str:
    n = len(s)
    if n == 0:
        return ""
    # 建立轉換字串：^#a#b#c#$（頭尾加哨兵避免邊界判斷）
    t = "^#" + "#".join(s) + "#$"
    m = len(t)
    p = [0] * m
    center = right = 0

    for i in range(1, m - 1):
        mirror = 2 * center - i
        if i < right:
            p[i] = min(right - i, p[mirror])

        # 繼續擴展
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1

        # 更新最右回文邊界
        if i + p[i] > right:
            center, right = i, i + p[i]

    # 找最大半徑，映射回原字串
    max_len, center_idx = 0, 0
    for i in range(1, m - 1):
        if p[i] > max_len:
            max_len = p[i]
            center_idx = i

    start = (center_idx - max_len) // 2
    return s[start:start + max_len]


# ============================================================
# 驗證與基準測試
# ============================================================

def brute_force(s: str) -> str:
    """暴力法：枚舉所有子串，挑最長的回文（僅供小字串驗證用）。"""
    n = len(s)
    best = ""
    for i in range(n):
        for j in range(i + 1, n + 1):
            sub = s[i:j]
            if sub == sub[::-1] and len(sub) > len(best):
                best = sub
    return best


def verify():
    print("=" * 60)
    print("三種演算法 + 暴力法 交叉驗證")
    print("=" * 60)

    cases = [
        "babad",
        "cbbd",
        "a",
        "",
        "ac",
        "forgeeksskeegfor",
        "abcba",
        "abacdfgdcaba",
        "aaaa",
        "abcddcba",
    ]

    rng = random.Random(42)
    for _ in range(20):
        length = rng.randint(1, 30)
        cases.append("".join(rng.choice("ab") for _ in range(length)))

    all_ok = True
    for s in cases:
        r_dp = longest_palindrome_dp(s)
        r_ex = longest_palindrome_expand(s)
        r_ma = longest_palindrome_manacher(s)
        r_bf = brute_force(s) if len(s) <= 40 else None

        len_dp, len_ex, len_ma = len(r_dp), len(r_ex), len(r_ma)

        # 三者長度必須相同（字串本身在有多解時可能不同，但長度必同）
        same_len = len_dp == len_ex == len_ma
        # 各自結果必須真的是回文
        is_pal = (r_dp == r_dp[::-1] and r_ex == r_ex[::-1]
                  and r_ma == r_ma[::-1])
        # 小字串再與暴力法比長度
        bf_ok = True if r_bf is None else (len(r_bf) == len_dp)

        ok = same_len and is_pal and bf_ok
        all_ok = all_ok and ok

        display = s if len(s) <= 40 else s[:37] + "..."
        print(f"  s = \"{display}\"")
        print(f"    DP={r_dp!r}({len_dp})  Expand={r_ex!r}({len_ex})"
              f"  Manacher={r_ma!r}({len_ma})  -> {'PASS' if ok else 'FAIL'}")

    print(f"\n  全部通過: {all_ok}")
    return all_ok


def benchmark():
    print()
    print("=" * 60)
    print("基準測試：隨機字串 (字母表大小=26)")
    print("=" * 60)
    print(f"  {'n':>6}  {'DP(ms)':>10}  {'Expand(ms)':>12}  "
          f"{'Manacher(ms)':>14}")
    print("  " + "-" * 48)

    rng = random.Random(7)
    for n in [100, 500, 1000, 2000, 4000]:
        s = "".join(rng.choice(string.ascii_lowercase) for _ in range(n))

        t0 = time.perf_counter()
        longest_palindrome_dp(s)
        t_dp = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        longest_palindrome_expand(s)
        t_ex = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        longest_palindrome_manacher(s)
        t_ma = (time.perf_counter() - t0) * 1000

        print(f"  {n:>6}  {t_dp:>10.3f}  {t_ex:>12.3f}  {t_ma:>14.3f}")


def demo_trace():
    print()
    print("=" * 60)
    print("逐步追蹤：s = \"forgeeksskeegfor\"")
    print("=" * 60)
    s = "forgeeksskeegfor"
    print(f"  DP        -> {longest_palindrome_dp(s)}")
    print(f"  中心擴展   -> {longest_palindrome_expand(s)}")
    print(f"  Manacher  -> {longest_palindrome_manacher(s)}")
    print(f"  最長回文 = \"geeksskeeg\"（長度 10，跨越中間的 \"ss\"）")


if __name__ == "__main__":
    verify()
    demo_trace()
    benchmark()
