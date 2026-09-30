"""
HW4 自訂問題 : 用迭代法求圓周率 π

延續課堂教材 iterative3.py 的精神 (同一個方程式、寫出多種迭代式，
比較哪一個收斂得快) ，本檔自訂一個問題 : 求 π。

π 沒有任何已知的封閉式 (closed form)，所以只能用「極限」逼近：

    π = lim  s(n)      讓 s(n) 逐步逼近 π

本檔實作 6 種迭代法，最後排成「要算到小數點後 k 位需要幾步」的
對照表，用來回答本作業的核心問題：

    同樣是迭代，【收斂階】差一階，要的步數就差一個數量級。

    線性收斂   (linear)      每步多 ~1 位小數     ->  要幾十步
    超線性     (superlinear) 每步多好幾位小數     ->  十幾步
    二次收斂   (quadratic)   正確位數每步平方     ->  3~5 步

各方法簡介 :
  1. Viete 連乘法  : 線性收斂，每步 +1 位小數
  2. Wallis 乘積    : 線性收斂，但誤差 ~ 1/(4n)，慢得離譜 (反面教材)
  3. Machin+Gregory : 線性收斂，每步 +1.4 位小數
  4. 牛頓法求根     : 二次收斂，把 cos(x/2)=0 的根逼向 π
  5. Aitken Δ² 加速 : 用外插把 Viete 從線性「加速」成超線性
  6. 蒙地卡羅法     : O(1/sqrt(N))，隨機模擬，當作最慢的對照組

執行 : python3 pi_iterative.py
"""

import math
import random

PI = math.pi                       # 標準答案，只用來「驗算」，不拿來算


# ============================================================
# 1. Viete 連乘法 (1593, Francois Viete)
#
#    2/pi = (sqrt2/2)·(sqrt(2+sqrt2)/2)·(sqrt(2+sqrt(2+sqrt2))/2)·...
#
#    寫成迭代式 :
#        a_0     = sqrt(2)
#        a_{k+1} = sqrt(2 + a_k)
#        pi_n    = 2 · prod_{k=0}^{n} (2 / a_k)
#
#    誤差 : a_k 以 1/2 的速度逼近 2，所以 pi_n 每多做一項大約多對
#           1 位小數 => 線性收斂，收斂因子約 0.5
# ============================================================
def viete_seq(N):
    """回傳 [pi_0, pi_1, ..., pi_N]，viete_seq(n) 做完 n 次迭代的近似值"""
    a = math.sqrt(2.0)
    p = 2.0 / a                     # 第 0 項 2/sqrt(2)
    out = [2.0 * p]
    for _ in range(N):
        a = math.sqrt(2.0 + a)
        p *= 2.0 / a
        out.append(2.0 * p)
    return out


# ============================================================
# 2. Wallis 乘積 (1656, John Wallis)
#
#    pi/2 = prod_{n=1..N} (2n)^2 / ((2n-1)(2n+1))
#
#    誤差 ~ pi/(4N)  =>  要對到小數點後 6 位需要 N 約 7.8 億項。
#    這就是 17~19 世紀數學家相信「π 不可能被算出來」的原因。
#    本函式只跑有限項，用來展示「慢」到底長什麼樣子。
# ============================================================
def wallis_seq(N):
    out = [2.0]
    p = 1.0
    for k in range(1, N + 1):
        p *= (2 * k) ** 2 / ((2 * k - 1) * (2 * k + 1))
        out.append(2.0 * p)
    return out


# ============================================================
# 3. Machin 公式 + Gregory 級數 (1706, John Machin)
#
#    pi/4 = 4·atan(1/5) - atan(1/239)
#    atan(1/m) = 1/m - 1/(3m^3) + 1/(5m^5) - 1/(7m^7) + ...
#
#    迭代式 : 每輪多加一項，剩餘項以 1/25 的速度被消掉
#             => 每步多對 log10(25) ~ 1.4 位小數，比 Viete 快一點
# ============================================================
def atan_inv(m, K):
    """atan(1/m) 的前 K 項 Gregory 級數"""
    total = 0.0
    power = 1.0 / m
    for k in range(K):
        total += (-1) ** k * power / (2 * k + 1)
        power /= m * m
    return total


def machin_seq(K):
    return [16.0 * atan_inv(5, k) - 4.0 * atan_inv(239, k) for k in range(K + 1)]


# ============================================================
# 4. 牛頓法求根 : cos(x/2) = 0
#
#    為什麼這樣就能拿到 π ?
#        cos(x/2) = 0  <=>  x/2 = pi/2 + m·pi  <=>  x = pi + 2m·pi
#    取 x_0 = 3 (落在 (0, 2pi) 內) 往下收斂，就會停在 x = pi。
#
#    牛頓迭代式 : x_{n+1} = x_n - f(x_n)/f'(x_n)
#                 f(x) = cos(x/2)  =>  f'(x) = -1/2 · sin(x/2)
#                 =>   x_{n+1} = x_n + 2·cos(x_n/2) / sin(x_n/2)
#
#    關鍵 : f'(pi) = -1/2 != 0 (不是重根)  =>  二次收斂成立
# ============================================================
def newton_seq(iters, x0=3.0):
    x = x0
    out = [x]
    for _ in range(iters):
        x = x + 2.0 * math.cos(x / 2.0) / math.sin(x / 2.0)
        out.append(x)
    return out


# ============================================================
# 5. Aitken Δ² 加速 (加速任何「線性收斂」的序列)
#
#    對線性收斂序列 s_n，可先估計收斂因子
#        lambda ~ (s_{n+1} - s_n) / (s_n - s_{n-1})
#    再往外插一步
#        s* = s_{n+1} - (s_{n+1} - s_n)·lambda / (1 - lambda)
#    等價的 Aitken Δ² 寫法 (程式採用這個)：
#        s* = s_n - (s_{n+1} - s_n)^2 / (s_{n+2} - 2·s_{n+1} + s_n)
#
#    效果 : Viete 原本一步只多 1 位小數，加速後變成一步多 3 位以上。
# ============================================================
def aitken(s0, s1, s2):
    den = s2 - 2.0 * s1 + s0
    if den == 0.0:
        return s1
    return s0 - (s1 - s0) ** 2 / den


def aitken_seq(viete, N):
    """用 Aitken Δ² 加速 Viete 序列的前 N 項"""
    return [aitken(viete[n], viete[n + 1], viete[n + 2]) for n in range(N + 1)]


# ============================================================
# 6. 蒙地卡羅法 (隨機撒點，O(1/sqrt(N)))
#
#    在單位正方形隨機取 N 個點，落在圓內的比例 × 4 ≈ pi
#    誤差 ~ 1/sqrt(N) : N 要大到 10^12 才能對到小數點後 6 位，
#    電腦上根本做不到 —— 用來對照「確定性迭代」有多吃香。
# ============================================================
def monte_carlo(N, seed=42):
    rng = random.Random(seed)
    inside = 0
    for _ in range(N):
        x = rng.random()
        y = rng.random()
        if x * x + y * y <= 1.0:
            inside += 1
    return 4.0 * inside / N


def monte_carlo_seq(points, seed=42):
    """依序把樣本數加倍, 順便觀察 1/sqrt(N) 的誤差下降"""
    out = []
    rng = random.Random(seed)
    inside = 0
    drawn = 0
    for target in points:
        while drawn < target:
            x = rng.random()
            y = rng.random()
            if x * x + y * y <= 1.0:
                inside += 1
            drawn += 1
        out.append(4.0 * inside / drawn)
    return out


# ============================================================
# 對照表 : 各種方法要算到小數點後 k 位，各需要幾步
# ============================================================
def first_hit(seq, tol, limit):
    """回傳序列中第一個誤差小於 tol 的索引 (索引 = 迭代步數)"""
    for n in range(1, min(limit, len(seq))):
        if abs(seq[n] - PI) < tol:
            return n
    return None


def table_compare():
    viete = viete_seq(200)
    wallis = wallis_seq(400000)
    machin = machin_seq(80)
    newton = newton_seq(12)
    aitken = aitken_seq(viete, 40)
    mc_n = [10_000, 100_000, 200_000, 400_000, 800_000,
            1_000_000, 2_000_000, 4_000_000]
    mc = monte_carlo_seq(mc_n)

    print(f"  {'目標誤差':<14}{'Viete':>8}{'Wallis':>10}{'Machin':>9}"
          f"{'牛頓法':>9}{'Aitken':>9}{'蒙地卡羅':>14}")
    print("  " + "-" * 73)

    for digits, tol in ((3, 1e-3), (6, 1e-6), (10, 1e-10), (13, 1e-13)):
        # 蒙地卡羅只跑到 400 萬顆點，用「誤差已達到 1e-3 的最小樣本數」代表
        n_mc = None
        for n, v in zip(mc_n, mc):
            if abs(v - PI) < tol:
                n_mc = n
                break

        cells = []
        for value, width in ((first_hit(viete, tol, 200), 8),
                             (first_hit(wallis, tol, 400000), 10),
                             (first_hit(machin, tol, 80), 9),
                             (first_hit(newton, tol, 12), 9),
                             (first_hit(aitken, tol, 40), 9)):
            text = "做不到" if value is None else f"{value:,}"
            cells.append(f"{text:>{width}}")

        mc_text = "做不到 (>400萬)" if n_mc is None else f"{n_mc:,} 顆點"
        print(f"  小數點後 {digits:>2} 位  " + "".join(cells) + f"{mc_text:>14}")

    print()
    print("  ※ 牛頓法 3 次就到 1e-13，這是二次收斂 (正確位數每步平方) 的威力。")
    print("  ※ Viete / Machin 都要十幾二十步，因為它們只是線性收斂。")
    print("  ※ Wallis 誤差 ~ 1/(4N)，要到 1e-6 需要 N ~ 7.85 億項，程式只跑 40 萬。")
    print("  ※ 蒙地卡羅的「步數」是丟幾顆隨機點，要 10 位小數需約 10^20 顆。")
    print()


# ============================================================
# 逐條展示每一種方法的收斂過程
# ============================================================
def show_viete():
    print("--- 1. Viete 連乘法 (線性收斂，每步 +1 位小數) ---")
    v = viete_seq(30)
    for n in (0, 1, 2, 3, 5, 10, 20, 30):
        print(f"    n={n:<3} pi={v[n]:.15f}  誤差={abs(v[n] - PI):.2e}")
    print()


def show_wallis():
    print("--- 2. Wallis 乘積 (線性收斂，但慢得離譜) ---")
    w = wallis_seq(100000)
    for n in (1, 10, 100, 1000, 10000, 100000):
        print(f"    N={n:<7} pi={w[n]:.15f}  誤差={abs(w[n] - PI):.2e}"
              f"   (理論 pi/4N = {PI / (4 * n):.2e})")
    print("    => 誤差每加 10 倍項數才降 10 倍；要小於 1e-6 需要 N 約 7.85 億。\n")


def show_machin():
    print("--- 3. Machin 公式 + Gregory 級數 (線性收斂，每步 +1.4 位) ---")
    m = machin_seq(10)
    for k in (1, 2, 3, 4, 5, 7, 9):
        print(f"    K={k:<3} pi={m[k]:.15f}  誤差={abs(m[k] - PI):.2e}")
    print()


def show_newton():
    print("--- 4. 牛頓法解 cos(x/2)=0 (二次收斂) ---")
    n = newton_seq(5)
    for i in range(1, len(n)):
        print(f"    第 {i} 次  x={n[i]:.15f}  誤差={abs(n[i] - PI):.2e}")
    print("    => 正確小數位數每步平方：1 -> 4 -> 12 -> 16 (撞上雙精度極限 ~1e-16)\n")


def show_aitken():
    print("--- 5. Aitken Δ² 加速 Viete (線性 -> 超線性) ---")
    v = viete_seq(14)
    a = aitken_seq(v, 12)
    for n in (0, 2, 4, 6, 8, 10):
        raw, fast = abs(v[n] - PI), abs(a[n] - PI)
        print(f"    n={n:<3} 原誤差={raw:.2e}   Aitken 誤差={fast:.2e}"
              f"   改善 {raw / fast:,.0f} 倍")
    print("    => Viete 原本要 21 步才對到 1e-13，加速後 8 步就到了。\n")


def show_monte_carlo():
    print("--- 6. 蒙地卡羅法 (O(1/sqrt(N))，最慢的對照組) ---")
    ns = [10_000, 100_000, 1_000_000, 4_000_000]
    for n, v in zip(ns, monte_carlo_seq(ns)):
        print(f"    N={n:>9,}  pi={v:.6f}  誤差={abs(v - PI):.2e}"
              f"   (理論 1/sqrt(N) = {1 / math.sqrt(n):.2e})")
    print("    => 400 萬顆點仍只對到 3 位小數；隨機法再怎麼砸資源都很慢。\n")


# ============================================================
# 自我測試 : 所有方法都必須逼近標準答案
# ============================================================
def self_test():
    print("--- 自我測試 : 各種方法是否都逼近 π ---")
    v = viete_seq(30)
    a = aitken_seq(v, 10)
    checks = [
        ("Viete   n=30", v[30], 1e-12),
        ("Wallis  N=100000", wallis_seq(100000)[100000], 1e-5),
        ("Machin  K=9", machin_seq(9)[9], 1e-12),
        ("牛頓法   4 次迭代", newton_seq(4)[4], 1e-12),
        ("Aitken  n=8", a[8], 1e-12),
        ("蒙地卡羅 N=1e6", monte_carlo(1_000_000), 1e-2),
    ]
    all_ok = True
    for name, value, tol in checks:
        ok = abs(value - PI) < tol
        all_ok = all_ok and ok
        print(f"  {name:<18} 估計值={value:.15f}  誤差={abs(value - PI):.2e}"
              f"  門檻={tol:g}  通過={ok}")
    print(f"  全部通過 : {all_ok}\n")


# ============================================================
# 7. 示範 : 直接套用 iter_framework.py 的通用框架
#    證明「牛頓法求 π」和框架裡的「牛頓法求根」是同一件事 :
#    transition = 一次牛頓推進, is_converged = 步長夠小就停
# ============================================================
def demo_with_framework():
    print("--- 7. 把牛頓法丟進 iter_framework 的通用框架 ---")
    try:
        import numpy as _np            # 只為了觸發 ImportError 檢查
        from iter_framework import generic_iterator
    except (ImportError, ModuleNotFoundError):
        print("    (需要同一目錄的 iter_framework.py 與 numpy，跳過這個示範)\n")
        return

    f = lambda x: math.cos(x / 2.0)
    df = lambda x: -0.5 * math.sin(x / 2.0)

    transition = lambda x: x - f(x) / df(x)
    converged = lambda old, new, i: abs(new - old) < 1e-14

    result, iters = generic_iterator(transition, converged,
                                     initial_state=3.0, max_iter=50)
    print(f"    框架求得 : pi = {result:.15f} (耗時 {iters} 次迭代)")
    print(f"    標準答案 : pi = {PI:.15f}")
    print(f"    誤差     : {abs(result - PI):.2e}")
    print("    => 同一個 generic_iterator，換一個 transition 就換了一個演算法。\n")


def main():
    print("=" * 62)
    print("  HW4 自訂問題 : 用迭代法求 π (對照收斂速度)")
    print("=" * 62 + "\n")

    show_viete()
    show_wallis()
    show_machin()
    show_newton()
    show_aitken()
    show_monte_carlo()

    print("=" * 62)
    print("  收斂速度總對照表")
    print("=" * 62 + "\n")
    table_compare()

    self_test()
    demo_with_framework()


if __name__ == "__main__":
    main()
