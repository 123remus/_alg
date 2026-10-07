"""
HW5-1 : 河內塔 (Tower of Hanoi)

同一問題、兩種解法：
  1. hanoi_recursive   -- 遞迴版 (標準解法)
  2. hanoi_iterative   -- 禁止遞迴版 (用顯式堆疊 stack 模擬遞迴)
  3. hanoi_parity      -- 禁止遞迴版 (用「奇偶方向 + 唯一合法步」的經典疊代法)

三種方法都會產生同一組最佳移動序列 (共 2^n - 1 步)，程式會互相驗證。
"""


# ------------------------------------------------------------------
# 1. 遞迴版
# ------------------------------------------------------------------
def hanoi_recursive(n, src="A", aux="B", dst="C"):
    """把 n 個盤子從 src 移到 dst，aux 為輔助柱。回傳移動序列。"""
    moves = []

    def solve(k, s, a, d):
        if k == 0:
            return
        solve(k - 1, s, d, a)   # 上面 k-1 個先搬到輔助柱
        moves.append((s, d))    # 最大的盤子搬過去
        solve(k - 1, a, s, d)   # 再把 k-1 個搬過來

    solve(n, src, aux, dst)
    return moves


# ------------------------------------------------------------------
# 2. 禁止遞迴版：顯式堆疊 (模擬上面的遞迴呼叫)
# ------------------------------------------------------------------
def hanoi_iterative(n, src="A", aux="B", dst="C"):
    """用一個 stack 取代遞迴呼叫堆疊。stack 裡放 (盤數, 來源, 輔助, 目的)。"""
    moves = []
    stack = [(n, src, aux, dst)]
    while stack:
        k, s, a, d = stack.pop()
        if k == 1:
            moves.append((s, d))
        else:
            # 注意堆疊是後進先出，所以要「倒著」放：
            # 先做 solve(k-1, s, d, a)，再做「移動」，最後 solve(k-1, a, s, d)
            stack.append((k - 1, a, s, d))   # 後做
            stack.append((1, s, a, d))       # 中間的移動
            stack.append((k - 1, s, d, a))   # 先做
    return moves


# ------------------------------------------------------------------
# 3. 禁止遞迴版：奇偶方向演化法
# ------------------------------------------------------------------
def hanoi_parity(n, src="A", aux="B", dst="C"):
    """
    經典疊代解法：
      - 盤數 n 為奇數時，最小盤在 A->C->B->A 之間循環；
      - 盤數 n 為偶數時，最小盤在 A->B->C->A 之間循環。
      - 每搬完最小盤，就做「唯一一個不違反規則」的其他移動。
    """
    pegs = {src: list(range(n, 0, -1)), aux: [], dst: []}
    names = [src, aux, dst]
    # 最小盤的循環方向
    if n % 2 == 1:
        ring = [src, dst, aux]           # A -> C -> B -> A
    else:
        ring = [src, aux, dst]           # A -> B -> C -> A
    pos = {name: i for i, name in enumerate(ring)}   # 各柱在 ring 中的索引

    moves = []
    smallest_peg = src
    total = 2 ** n - 1

    for _ in range(total):
        # ① 移動最小盤：到循環中的下一根柱子
        nxt = ring[(pos[smallest_peg] + 1) % 3]
        pegs[smallest_peg].pop()
        pegs[nxt].append(1)
        moves.append((smallest_peg, nxt))
        smallest_peg = nxt

        if len(moves) == total:
            break

        # ② 在另外兩根柱子間做唯一合法移動 (不能把大盤放到小盤上)
        others = [p for p in names if p != smallest_peg]
        x, y = others
        top_x = pegs[x][-1] if pegs[x] else float("inf")
        top_y = pegs[y][-1] if pegs[y] else float("inf")
        if top_x < top_y:
            pegs[y].append(pegs[x].pop())
            moves.append((x, y))
        else:
            pegs[x].append(pegs[y].pop())
            moves.append((y, x))
    return moves


# ------------------------------------------------------------------
# 驗證
# ------------------------------------------------------------------
def is_legal(moves, n, src, aux, dst):
    """逐步模擬，檢查每一步 (1) 有盤子可搬 (2) 沒有大盤壓小盤。"""
    pegs = {src: list(range(n, 0, -1)), aux: [], dst: []}
    for f, t in moves:
        if not pegs[f]:
            return False
        disk = pegs[f].pop()
        if pegs[t] and pegs[t][-1] < disk:
            return False
        pegs[t].append(disk)
    return pegs[dst] == list(range(n, 0, -1))


def show_moves(moves, title):
    print(f"{title} (共 {len(moves)} 步):")
    for i, (f, t) in enumerate(moves, 1):
        print(f"  {i:>2}. {f} -> {t}")


def main():
    print("=" * 60)
    print("河內塔：遞迴 vs 禁止遞迴")
    print("=" * 60)

    for n in range(1, 6):
        r = hanoi_recursive(n)
        it = hanoi_iterative(n)
        pa = hanoi_parity(n)
        same = (r == it == pa)
        legal = (is_legal(r, n, "A", "B", "C")
                 and is_legal(it, n, "A", "B", "C")
                 and is_legal(pa, n, "A", "B", "C"))
        print(f"n={n}: 步數={len(r):>2} (預期 {2**n-1:>2})  "
              f"遞迴==堆疊==奇偶: {same}  三種皆合法: {legal}")

    print("\n" + "-" * 60)
    n = 4
    show_moves(hanoi_recursive(n), f"n={n} 的移動序列")
    print("-" * 60)

    print("\n最佳移動步數 = 2^n - 1")
    print(f"  n:   " + "".join(f"{i:>14}" for i in range(1, 11)))
    print(f"  步數:" + "".join(f"{2**i-1:>14,}" for i in range(1, 11)))


if __name__ == "__main__":
    main()
