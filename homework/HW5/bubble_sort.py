"""
HW5-3 : 自製 map / filter / reduce，並在「禁止使用迴圈」的前提下完成泡沫排序。

規則：
  * 不可以使用 for / while
  * 所有重複性工作改用「遞迴」與自製的 my_map / my_filter / my_reduce
"""

_MISSING = object()


# ==================================================================
# 1. 自製 map / filter / reduce
# ==================================================================
def my_reduce(func, seq, init=_MISSING):
    """自製 reduce：seq 為空時回傳 init；未給 init 則以第一個元素為初始值。"""
    data = list(seq)
    if init is _MISSING:
        if not data:
            raise TypeError("reduce() of empty sequence with no initial value")
        acc, rest = data[0], data[1:]
    else:
        acc, rest = init, data

    def go(acc, rest):
        if not rest:
            return acc
        return go(func(acc, rest[0]), rest[1:])

    return go(acc, rest)


def my_map(func, seq):
    """自製 map：把 func 套用到每個元素，回傳 list。"""
    return my_reduce(lambda acc, x: acc + [func(x)], list(seq), [])


def my_filter(pred, seq):
    """自製 filter：留下 pred 為真的元素，回傳 list。"""
    return my_reduce(lambda acc, x: acc + [x] if pred(x) else acc, list(seq), [])


# ==================================================================
# 2. 泡沫排序 (禁止迴圈)
# ==================================================================
def bubble_pass(lst):
    """
    一趟泡沫排序：從左到右把「目前為止最大的數」往右推。
    用 my_reduce 掃描：carry 是目前正在往右冒泡的數值。
    回傳 (新 list, 這趟是否有交換)。
    """
    if len(lst) <= 1:
        return list(lst), False

    def step(acc, x):
        out, carry, swapped = acc
        if carry <= x:                      # 順序正確：carry 固定下來，改由 x 冒泡
            return (out + [carry], x, swapped)
        else:                               # 逆序：交換，較大的 carry 繼續往右
            return (out + [x], carry, True)

    out, carry, swapped = my_reduce(step, lst[1:], ([], lst[0], False))
    return out + [carry], swapped


def bubble_sort(lst):
    """反覆做 bubble_pass，直到某一趟完全沒有交換 (代表已排序)。用遞迴取代迴圈。"""
    def loop(arr):
        arr2, swapped = bubble_pass(arr)
        if not swapped:
            return arr2
        return loop(arr2)

    return loop(list(lst))


# ==================================================================
# 3. 驗證工具 (照樣不用迴圈)
# ==================================================================
def is_sorted(lst):
    """檢查是否為升序：用 my_reduce 掃過所有相鄰配對。"""
    if len(lst) <= 1:
        return True
    pairs = list(zip(lst, lst[1:]))
    return my_reduce(lambda ok, p: ok and p[0] <= p[1], pairs, True)


# ==================================================================
# 4. 示範
# ==================================================================
def show_map_filter_reduce():
    print("=" * 60)
    print("自製 my_map / my_filter / my_reduce 示範")
    print("=" * 60)
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    print(f"原始資料           : {data}")
    print(f"my_map(x^2)        : {my_map(lambda x: x * x, data)}")
    print(f"my_filter(偶數)    : {my_filter(lambda x: x % 2 == 0, data)}")
    print(f"my_reduce(+)       : {my_reduce(lambda a, b: a + b, data)}")
    print(f"my_reduce(*, init=1): {my_reduce(lambda a, b: a * b, data, 1)}")
    print()


def main():
    show_map_filter_reduce()

    print("=" * 60)
    print("泡沫排序 (禁止迴圈)")
    print("=" * 60)

    tests = [
        [5, 2, 9, 1, 5, 6],
        [3, 1, 2],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [42],
        [],
        [7, 7, 7, 2, 2, 9, 0, -1, 15, -3],
    ]
    for t in tests:
        s = bubble_sort(t)
        print(f"  {str(t):<32} -> {str(s):<32} (升序: {is_sorted(s)})")

    print("\n補充：把三個自製工具串起來")
    print("  (先篩出偶數 -> 平方 -> 泡沫排序)")
    seq = [9, 2, 7, 4, 6, 1, 8, 3]
    result = bubble_sort(my_map(lambda x: x * x,
                                my_filter(lambda x: x % 2 == 0, seq)))
    print(f"  {seq} -> {result}")


if __name__ == "__main__":
    main()
