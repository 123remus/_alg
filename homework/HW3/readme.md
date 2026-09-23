# HW3 : 系統性列舉真值表，暴力解決 SAT 問題

本作業實作一個**暴力列舉真值表**的 SAT 求解器，對任意布林公式，把變數所有
True/False 組合全部列出來，一列一列代進公式算，只要有任一列為 True 就算「可滿足」。

## SAT 問題是什麼？

SAT（Boolean Satisfiability Problem，布林可滿足性問題）：
給定一個布林公式，問「是否存在一組變數指派，讓整個公式為 True」。
- **存在** → SATISFIABLE（可滿足），並可列出所有可行指派。
- **不存在** → UNSATISFIABLE（不可滿足）。

它是最經典的 **NP-complete** 問題之一，參考：
https://en.wikipedia.org/wiki/Boolean_satisfiability_problem

## 執行方式

```bash
python3 sat.py                # 跑內建的 4 組範例 + 隨機 3-SAT 比較
python3 sat.py "(a|b)&(~a|c)" # 直接解你給的任意公式
```

支援的運算子（由低到高優先權）：

| 運算子 | 寫法 | 說明 |
|--------|------|------|
| `->`   | `->` `=>` `implies` | 蘊含，`a->b` 等價 `not a or b` |
| `or`   | `or` `|` `||` | 邏輯或 |
| `xor`  | `xor` `^` | 互斥或 |
| `and`  | `and` `&` `&&` | 邏輯且 |
| `not`  | `not` `!` | 邏輯非 |
| `()`   | 括號 | 改變優先權 |
| 常數   | `true` `false` `1` `0` | 真/假 |

## 核心方法：系統性列舉真值表

1. 把公式 parse 成**語法樹（AST）**。
2. 找出公式中所有變數，共 n 個。
3. 用 `mask` 從 `0` 數到 `2^n - 1`，`mask` 的第 i 個 bit 就是第 i 個變數的值，
   系統性地窮舉出 **2^n** 種指派（整張真值表）。例如 n=3：

   ```
   mask = 000, 001, 010, 011, 100, 101, 110, 111
         a,b,c 每一種 True/False 組合都不漏　
   ```

4. 每一列代入公式求值，只要有一列算出來是 True 就找到解。

```python
def enumerate_assignments(vars_):
    n = len(vars_)
    for mask in range(1 << n):                       # 2^n 種指派
        assign = {v: bool((mask >> i) & 1) for i, v in enumerate(vars_)}
        yield mask, assign

def solve_sat(node, vars_):
    table = [(m, a, evaluate(node, a)) for m, a in enumerate_assignments(vars_)]
    models = [(m, a) for m, a, v in table if v]
    return (len(models) > 0), models, table
```

## 執行輸出（節錄）

有解公式 `(a or b) and (not a or c) and (b or not c)`：

```
  a   b   c   結果
  -----------------
  F  F  F   F
  T  F  F   F
  F  T  F   T  <== 找到解
  ...
  => 3 個變數，共列出 2^3 = 8 列指派
  => 有 3 列結果為 True  =>  SATISFIABLE (可滿足)
      可行指派 : F  T  F  (bit 010)
      可行指派 : F  T  T  (bit 110)
      可行指派 : T  T  T  (bit 111)
```

無解公式 `a and b and (not a or not b)`（要求 a=True、b=True，但又不能同時為真）：

```
  a   b   結果
  -------------
  F  F   F
  T  F   F   ... 每一列都是 False ...
  => 有 0 列結果為 True  =>  UNSATISFIABLE (不可滿足)
```

## 進階功能（順便比較效能）

### 1. 從真值表反向生成等價 CNF / DNF
- 每一列「結果為 False」→ 生一個子句推翻該列 → 全部 AND 起來就是**等價 CNF**。
- 每一列「結果為 True」→ 生一個項命中該列 → 全部 OR 起來就是**等價 DNF**。

### 2. DPLL（回溯 + 單元傳播）當對照組
暴力列舉必須看完 2^n 列才敢斷言，DPLL 靠「單元傳播 + 剪枝」只走一小部分。

隨機 3-SAT（16 變數、24 子句）實測：

```
  [暴力列舉] 檢查到第 17 列就找到解, 最壞需看 2^16 = 65,536 列
  [DPLL     ] 走訪 15 節點 (遠小於 65,536)
  驗證 DPLL 的指派真正滿足全部 24 條子句 : True
```

程式最後還有 5 組公式的自我測試，確認「暴力列舉」與「DPLL」的答案完全一致：
```
  全部一致 : True
```

## 時間複雜度

| 方法 | 時間複雜度 | 記憶體 | 說明 |
|------|------------|--------|------|
| 暴力列舉真值表 | O(2^n · 公式長度) | O(2^n)（若存整張表） | 最暴力、最直接、保證正確 |
| DPLL | 最壞仍 O(2^n)，通常遠低於 | O(n) | 靠單元傳播與剪枝省時間 |
| 暴力列舉 + 邊列舉邊檢查 | O(2^n · 公式長度) | O(1)（不存表） | 只需記住「有沒有找到解」 |

## 結論

- **列真值表**是解 SAT 最簡單、最不容易出錯的方法，非常適合小 n（例如 n ≤ 20）。
- 因為要試 **2^n** 種組合，n 稍微變大就會指數爆炸，這正是 SAT 屬於
  NP 問題的根本原因，也是目前還沒有已知多項式演算法的原因。
- DPLL、CDCL 等現代 SAT solver 本質上仍在「搜尋同一張真值表」，
  只是用聰明的剪枝跳過大量注定失敗的列；本程式的比較示範了這點。

> 課程：演算法 (115 學年上學期) — _alg 課堂作業 HW3