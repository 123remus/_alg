# HW6: Lambda Calculus Interpreter

一個能顯示完整計算過程的 Lambda Calculus 解譯器。

## 檔案

- `lambda_calculus.py` - 核心解譯器（Named + De Bruijn 轉換）
- `interpreter.py` - 命令列介面
- `sample_programs.py` - 範例程式（identity, SKI, Church numerals 等）
- `demo.py` - 基本展示
- `demo_complete.py` - 完整展示（含計算步驟、De Bruijn 轉換）
- `README.md` - 說明文件

## 功能特色

- **顯示完整歸約過程**：逐步印出每一次 beta reduction 的結果
- **Named representation（有名稱）**：使用變數名稱，易於理解
- **De Bruijn index（無名稱）**：內部轉換為 de Bruijn 索引表示
- **Normal order reduction（最左外部歸約）**：符合一般 Lambda Calculus 教學
- **Capture-avoiding substitution（避免變數捕捉）**：正確處理 alpha-renaming
- **豐富範例**：identity、true/false、SKI combinators、布林邏輯、Church numerals 等

## 使用方式

### 1. 執行完整展示

```bash
cd homework/HW6
python3 demo_complete.py
```

### 2. 命令列執行

```bash
python3 interpreter.py "(\x.\y.x y)(\z.z)"
```

### 3. 在 Python 程式中使用

```python
from lambda_calculus import NamedEvaluator

ev = NamedEvaluator(show_steps=True)
result = ev.eval_from_string(r"(\x.\y.x y)(\z.z)")
```

## 範例輸出

```text
Initial: ((\x.(\y.(x y))) (\z.z))
Step 1: (\y.((\z.z) y))
Step 2: (\y.y)
Normal form reached (2 steps)
Result: (\y.y)
```

## 範例程式

`sample_programs.py` 包含多個常用的 Lambda 項：

- `identity/I`: `(\x.x)`
- `true/K`: `(\x.\y.x)`, `false/K2`: `(\x.\y.y)`
- `S`: `(\f.\g.\x.f x (g x))`
- `SKK`: `(\f.\g.\x.f x (g x))(\x.\y.x)(\x.\y.x)` → 歸約為 identity
- `omega`: `(\x.x x)(\x.x x)`（會無限歸約，程式設有 max_steps 限制）
- 布林邏輯：`not`, `and`, `or`
- Church numerals：`zero`, `one`, `two`, `succ`, `plus`

