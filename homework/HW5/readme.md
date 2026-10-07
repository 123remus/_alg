# HW5：遞迴與反遞迴 — 河內塔、符號微分、自製 map/filter/reduce 泡沫排序

本作業分三部分，主題都是「**用遞迴（或反過來禁止遞迴）解決問題**」：

| 檔案 | 內容 |
|------|------|
| `hanoi.py` | 河內塔：**遞迴版**與**兩種禁止遞迴版**（顯式堆疊、奇偶方向法），並互相驗證 |
| `sym_diff.py` | **用遞迴實作符號微分** `sym_diff(expr)`：內含中序剖析器、微分法則、化簡、求值與數值驗證 |
| `bubble_sort.py` | **自製 `my_map` / `my_filter` / `my_reduce`**，並在**完全不用迴圈**的前提下完成泡沫排序 |
| `readme.md` | 本說明文件 |

## 執行方式

```bash
python3 hanoi.py         # 河內塔：遞迴 vs 禁止遞迴
python3 sym_diff.py      # 符號微分 sym_diff(expr)
python3 bubble_sort.py   # 自製 map/filter/reduce + 無迴圈泡沫排序
```

> 僅使用 Python 標準函式庫（`math`），無需額外套件。

---

## 1. 河內塔：遞迴 vs 禁止遞迴（`hanoi.py`）

問題：把 `n` 個盤子從來源柱 `A` 全部搬到目的柱 `C`，一次只能搬一個，且大盤子不能壓在小盤子上面。

### 1.1 遞迴版（標準解法）

遞迴的關鍵想法：**先把上面 `n-1` 個搬到輔助柱、搬最大盤、再把 `n-1` 個搬過來**。

```python
def hanoi_recursive(n, src, aux, dst):
    moves = []
    def solve(k, s, a, d):
        if k == 0:
            return
        solve(k - 1, s, d, a)   # ① 上面 k-1 個：src -> aux
        moves.append((s, d))    # ② 最大的盤子：src -> dst
        solve(k - 1, a, s, d)   # ③ 上面 k-1 個：aux -> dst
    solve(n, src, aux, dst)
    return moves
```

- 遞迴式：`T(n) = 2T(n-1) + 1`，`T(1)=1` ⟹ `T(n) = 2ⁿ − 1`。
- 這也證明**最少步數就是 2ⁿ − 1**，而且移動序列唯一。

### 1.2 禁止遞迴版 (一)：顯式堆疊模擬

既然遞迴只是「編譯器幫我們維護一個呼叫堆疊」，那就自己用 `stack` 維護。
把每個待辦事項 `(盤數, 來源, 輔助, 目的)` 推入堆疊；因為堆疊是**後進先出**，
所以推入順序要跟執行順序相反：

```python
def hanoi_iterative(n, src, aux, dst):
    moves = []
    stack = [(n, src, aux, dst)]
    while stack:
        k, s, a, d = stack.pop()
        if k == 1:
            moves.append((s, d))
        else:
            stack.append((k - 1, a, s, d))   # ③ 後做
            stack.append((1, s, a, d))       # ② 中間的移動
            stack.append((k - 1, s, d, a))   # ① 先做
    return moves
```

產生的序列與遞迴版**逐一步完全相同**。

### 1.3 禁止遞迴版 (二)：奇偶方向法

最經典的「不用堆疊」疊代解法，只需遵守兩條規則：

1. **最小盤**（編號 1）每一步都往同一個方向循環搬：
   - `n` 為**奇數**：`A → C → B → A`
   - `n` 為**偶數**：`A → B → C → A`
2. 搬完最小盤後，在另外兩柱之間做**唯一一個合法**的移動（不能大壓小）。

```python
if n % 2 == 1:
    ring = [src, dst, aux]           # A -> C -> B -> A
else:
    ring = [src, aux, dst]           # A -> B -> C -> A
```

這方法不需要任何遞迴、也不需要額外堆疊，迴圈 `2ⁿ − 1` 次即完成。

### 1.4 三種方法互相驗證（實際輸出）

程式對 `n = 1..5` 分別用三種方法求解，並檢查「序列相同」與「每一步都合法（沒有大盤壓小盤、最後全部到 C）」：

```text
============================================================
河內塔：遞迴 vs 禁止遞迴
============================================================
n=1: 步數= 1 (預期  1)  遞迴==堆疊==奇偶: True  三種皆合法: True
n=2: 步數= 3 (預期  3)  遞迴==堆疊==奇偶: True  三種皆合法: True
n=3: 步數= 7 (預期  7)  遞迴==堆疊==奇偶: True  三種皆合法: True
n=4: 步數=15 (預期 15)  遞迴==堆疊==奇偶: True  三種皆合法: True
n=5: 步數=31 (預期 31)  遞迴==堆疊==奇偶: True  三種皆合法: True

------------------------------------------------------------
n=4 的移動序列 (共 15 步):
   1. A -> B      2. A -> C      3. B -> C      4. A -> B      5. C -> A
   6. C -> B      7. A -> B      8. A -> C      9. B -> C     10. B -> A
  11. C -> A     12. B -> C     13. A -> B     14. A -> C     15. B -> C
------------------------------------------------------------
```

**結論**：遞迴版與兩種禁止遞迴版產生**完全相同的唯一最佳解**，步數皆為 `2ⁿ − 1`。

---

## 2. 用遞迴做符號微分 `sym_diff(expr)`（`sym_diff.py`）

符號微分的本質是對「數學式的樹狀結構」遞迴地套用微分法則。本程式把數學式表示成
**抽象語法樹 (AST)**，節點是巢狀 tuple：

| 節點 | 意義 | 節點 | 意義 |
|------|------|------|------|
| `('num', v)` | 常數 `v` | `('pow', a, b)` | `aᵇ` |
| `('var', 'x')` | 變數 `x` | `('neg', a)` | `-a` |
| `('add', a, b)` | `a + b` | `('sin'/'cos'/'tan'/'exp'/'ln'/'sqrt', a)` | 函式 |
| `('sub', a, b)` | `a - b` | `('mul'/'div', a, b)` | 乘 / 除 |

### 2.1 三層架構

1. **剖析器 `parse(str)`**：遞迴下降語法分析（`expr → term → factor → unary → primary`），支援 `+ - * / ^`（含 `**`）、括號、一元負號與函式 `sin cos tan exp ln sqrt`。
2. **微分核心 `sym_diff(expr)`**：遞迴走訪 AST，套用法則後回傳導函式。輸入可以是字串或 AST。
3. **化簡 `simplify()`**：把 `0+a`、`1*a`、`a-0`、`f¹` 之類的雜訊清掉，讓結果乾淨。

### 2.2 遞迴微分法則（節錄）

```python
if tag == "add":                                  # 和差法則
    return ("add", _diff(a, var), _diff(b, var))
if tag == "mul":                                  # 乘法法則 (fg)' = f'g + fg'
    return ("add", ("mul", _diff(f, var), g), ("mul", f, _diff(g, var)))
if tag == "div":                                  # 除法法則 (f/g)'
    return ("div", ("sub", ("mul", _diff(f,var), g), ("mul", f, _diff(g,var))),
            ("pow", g, ("num", 2.0)))
if tag == "pow" and exp[0] == "num":              # 冪次法則 (fⁿ)' = n·fⁿ⁻¹·f'
    n = exp[1]
    return ("mul", ("mul", ("num", n), ("pow", base, ("num", n-1))), _diff(base, var))
if tag == "sin":                                  # 連鎖法則 (sin f)' = cos f · f'
    return ("mul", ("cos", e[1]), _diff(e[1], var))
```

`pow` 若指數不是常數（例如 `x^x`）則使用推廣式
`(fᵍ)' = fᵍ · (g'·ln f + g·f'/f)`。

### 2.3 數值驗證

對每個例子，程式比較**符號微分結果**與**中央差分** `(f(x+h) − f(x−h)) / 2h` 在 `x=0.7` 的值。

實際輸出：

```text
f(x)  = 3 * x ^ 2 + 2 * x - 5
f'(x) = 3 * 2 * x + 2
  驗證 x=0.7: 符號=6.2000000000  數值=6.2000000003  誤差=2.89e-10

f(x)  = x ^ 2 * sin(x)
f'(x) = 2 * x * sin(x) + x ^ 2 * cos(x)
  驗證 x=0.7: 符號=1.2766774339  數值=1.2766774339  誤差=3.46e-11

f(x)  = sin(x ^ 2)
f'(x) = cos(x ^ 2) * 2 * x
  驗證 x=0.7: 符號=1.2352660021  數值=1.2352660021  誤差=4.34e-11

f(x)  = exp(x) / (1 + x ^ 2)
f'(x) = (exp(x) * (1 + x ^ 2) - exp(x) * 2 * x) / (1 + x ^ 2) ^ 2
  驗證 x=0.7: 符號=0.0816349460  數值=0.0816349459  誤差=1.12e-10

f(x)  = tan(x)
f'(x) = 1 / cos(x) ^ 2
  驗證 x=0.7: 符號=1.7094497159  數值=1.7094497159  誤差=8.44e-11

f(x)  = x ^ x
f'(x) = x ^ x * (ln(x) + x / x)
  驗證 x=0.7: 符號=0.5011861887  數值=0.5011861887  誤差=2.36e-11
```

所有誤差都在 `1e-10` 量級（差分法的截斷誤差範圍內），證明符號微分結果正確。

程式還能**對導函式再微分**得到二階導數：

```text
f   = x ^ 3 * sin(x)
f'  = 3 * x ^ 2 * sin(x) + x ^ 3 * cos(x)
f'' = 3 * 2 * x * sin(x) + 3 * x ^ 2 * cos(x) + 3 * x ^ 2 * cos(x) + x ^ 3 * -sin(x)
```

**結論**：`sym_diff` 本身就是一個遞迴函式，每一條微分法則都對應「子樹的遞迴呼叫」，
完全體現「符號運算 = 樹的遞迴遍歷」這個核心觀念。

---

## 3. 自製 map/filter/reduce + 無迴圈泡沫排序（`bubble_sort.py`）

題目要求：**自己寫出 `map`、`filter`、`reduce`，然後不准用迴圈完成泡沫排序。**

### 3.1 自製三個高階函式（全部靠遞迴，不用 for/while）

```python
def my_reduce(func, seq, init=_MISSING):
    data = list(seq)
    if init is _MISSING:
        acc, rest = data[0], data[1:]      # 沒給 init 就用第一個元素當初始值
    else:
        acc, rest = init, data
    def go(acc, rest):
        if not rest:
            return acc
        return go(func(acc, rest[0]), rest[1:])   # 遞迴取代迴圈
    return go(acc, rest)

def my_map(func, seq):
    return my_reduce(lambda acc, x: acc + [func(x)], list(seq), [])

def my_filter(pred, seq):
    return my_reduce(lambda acc, x: acc + [x] if pred(x) else acc, list(seq), [])
```

注意 `my_map` / `my_filter` 都是「**用 `my_reduce` 疊出來的**」，三個函式共用同一套遞迴引擎。

### 3.2 泡沫排序（禁止迴圈）

泡沫排序的結構是「反覆做一趟掃描，直到某趟沒有任何交換」：

- **一趟掃描**用 `my_reduce` 完成：狀態 `carry` 是「正在往右冒泡的最大值」，
  由左往右兩兩比較；若逆序就交換，並把較大者繼續往右帶。
- **反覆做**則用**遞迴** `loop()` 取代 `while`。

```python
def bubble_pass(lst):
    if len(lst) <= 1:
        return list(lst), False
    def step(acc, x):
        out, carry, swapped = acc
        if carry <= x:                       # 順序正確
            return (out + [carry], x, swapped)
        return (out + [x], carry, True)      # 逆序 -> 交換，大的繼續往右
    out, carry, swapped = my_reduce(step, lst[1:], ([], lst[0], False))
    return out + [carry], swapped

def bubble_sort(lst):
    def loop(arr):
        arr2, swapped = bubble_pass(arr)
        return arr2 if not swapped else loop(arr2)   # 遞迴取代 while
    return loop(list(lst))
```

連「檢查是否已排序」也刻意不使用迴圈：

```python
def is_sorted(lst):
    pairs = list(zip(lst, lst[1:]))
    return my_reduce(lambda ok, p: ok and p[0] <= p[1], pairs, True)
```

### 3.3 實際輸出

```text
============================================================
自製 my_map / my_filter / my_reduce 示範
============================================================
原始資料           : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
my_map(x^2)        : [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
my_filter(偶數)    : [2, 4, 6, 8, 10]
my_reduce(+)       : 55
my_reduce(*, init=1): 3628800

============================================================
泡沫排序 (禁止迴圈)
============================================================
  [5, 2, 9, 1, 5, 6]                 -> [1, 2, 5, 5, 6, 9]                 (升序: True)
  [3, 1, 2]                          -> [1, 2, 3]                          (升序: True)
  [1, 2, 3, 4, 5]                    -> [1, 2, 3, 4, 5]                    (升序: True)
  [5, 4, 3, 2, 1]                    -> [1, 2, 3, 4, 5]                    (升序: True)
  [42]                               -> [42]                               (升序: True)
  []                                 -> []                                 (升序: True)
  [7, 7, 7, 2, 2, 9, 0, -1, 15, -3]  -> [-3, -1, 0, 2, 2, 7, 7, 7, 9, 15]  (升序: True)

補充：把三個自製工具串起來
  (先篩出偶數 -> 平方 -> 泡沫排序)
  [9, 2, 7, 4, 6, 1, 8, 3] -> [4, 16, 36, 64]
```

**結論**：整支程式沒有任何 `for` / `while`，所有重複動作都由「遞迴 + 自製
`my_map` / `my_filter` / `my_reduce`」完成，泡沫排序在各種輸入（含空list、
單一元素、已排序、全逆序、有重複值）都正確。

---

## 4. 總結

| 題目 | 用到的核心觀念 | 遞迴關係 |
|------|----------------|----------|
| 河內塔（遞迴） | 分治：`n-1` 子問題 + 1 + `n-1` 子問題 | `T(n)=2T(n-1)+1 → O(2ⁿ)` |
| 河內塔（禁止遞迴） | 顯式堆疊模擬 / 奇偶方向疊代 | 無 |
| 符號微分 `sym_diff` | 樹狀結構的遞迴遍歷 + 微分/連鎖法則 | 每個節點遞迴其子樹 |
| 泡沫排序（禁止迴圈） | 自製 `reduce` 掃描一趟 + 遞迴取代外層迴圈 | 每趟 `O(n)`，最壞 `O(n²)` |

一句話總結：**遞迴是把問題拆成同構的子問題；而「禁止遞迴」不是不能用堆疊，
只是要求我們自己把那份堆疊或狀態顯式地管好。**

> 課程：演算法 (115 學年上學期) — _alg 課堂作業 HW5，學生 許博翔 (111310508)
