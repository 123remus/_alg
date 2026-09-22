"""
HW2 : 求解下列遞迴方程式，並找出對應的演算法複雜度 (精確數字 + Big O)

  1.  T(n) = T(n-1) + 8,     T(1) = 1
  2.  T(n) = 2T(n-1) + 9,    T(1) = 1
  3.  T(n) = 2T(n/2) + 1,    T(1) = 1
  4.  T(n) = T(n/2) + 1,     T(1) = 1

每個題目都用兩種方式對照：
  (a) 直接照遞迴式迭代算出真實數字        (ground truth)
  (b) 代入「解出來的封閉公式」            (想驗證的答案)
若兩者數字完全一樣，代表公式解正確。
"""

import math

# ------------------------------------------------------------
# (a) 照遞迴定義直接迭代 ---- 當「對照組」
# ------------------------------------------------------------

def true_1(n):                      # T(n) = T(n-1)+8, T(1)=1
    t = 1
    for _ in range(n - 1):
        t += 8
    return t


def true_2(n):                      # T(n) = 2T(n-1)+9, T(1)=1
    t = 1
    for _ in range(n - 1):
        t = 2 * t + 9
    return t


def true_3(n):                      # T(n) = 2T(n/2)+1, T(1)=1, 限 n=2^k
    t, m = 1, 1
    while m < n:
        t = 2 * t + 1
        m *= 2
    return t


def true_4(n):                      # T(n) = T(n/2)+1, T(1)=1, 限 n=2^k
    t, m = 1, 1
    while m < n:
        t = t + 1
        m *= 2
    return t


# ------------------------------------------------------------
# (b) 解出來的封閉公式 ---- 想要驗證的答案
# ------------------------------------------------------------

def closed_1(n):                    # 展開 n-1 次 : T(1) + 8(n-1)
    return 8 * n - 7


def closed_2(n):                    # T(n) = 2^(n-1)T(1) + 9(2^(n-1)-1)
    return 5 * (2 ** n) - 9         #     = 5·2^n - 9


def closed_3(n):                    # 每層 +1 但呼叫加倍 : T(n)=2^{k+1}-1
    return 2 * n - 1


def closed_4(n):                    # 每層 n 減半、各層 +1，共 log2 n 層
    return int(math.log2(n)) + 1


# ------------------------------------------------------------
# 驗證 + 輸出
# ------------------------------------------------------------

def verify(name, true_f, closed_f, ns):
    print(f"  {'n':>5} | {'照遞迴迭代':>14} | {'封閉公式':>14} | {'驗證':>4}")
    print(f"  -------+----------------+----------------+------")
    ok = True
    for n in ns:
        t = true_f(n)
        c = closed_f(n)
        same = (t == c)
        ok = ok and same
        print(f"  {n:>5} | {t:>14,} | {c:>14,} | {'OK' if same else 'FAIL'}")
    print(f"  => 封閉公式與遞迴完全一致 : {ok}\n")
    return ok


def main():
    print("=" * 62)
    print("遞迴方程式求解驗證")
    print("=" * 62)

    print("\n#1  T(n) = T(n-1) + 8,  T(1)=1   封閉解: T(n) = 8n - 7")
    verify("1", true_1, closed_1, range(1, 12))

    print("#2  T(n) = 2T(n-1) + 9, T(1)=1   封閉解: T(n) = 5·2^n - 9")
    verify("2", true_2, closed_2, range(1, 12))

    print("#3  T(n) = 2T(n/2) + 1, T(1)=1   封閉解: T(n) = 2n - 1  (n=2^k)")
    verify("3", true_3, closed_3, [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])

    print("#4  T(n) = T(n/2) + 1,  T(1)=1   封閉解: T(n) = log2(n) + 1  (n=2^k)")
    verify("4", true_4, closed_4, [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])

    print("=" * 62)
    print("複雜度結論 (Big O)")
    print("=" * 62)
    print("  #1  T(n) = 8n - 7            =>  O(n)      (線性)")
    print("  #2  T(n) = 5·2^n - 9         =>  O(2^n)    (指數)")
    print("  #3  T(n) = 2n - 1            =>  O(n)      (線性, 主定理 case1)")
    print("  #4  T(n) = log2(n) + 1       =>  O(log n)  (對數, 主定理 case2)")


if __name__ == "__main__":
    main()