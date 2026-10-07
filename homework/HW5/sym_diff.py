"""
HW5-2 : 符號數學式微分 (Symbolic Differentiation)

用遞迴對「數學式」微分。數學式以抽象語法樹 (AST, 巢狀 tuple) 表示：

    ('num', 3)              常數
    ('var', 'x')            變數
    ('add', a, b)           a + b
    ('sub', a, b)           a - b
    ('mul', a, b)           a * b
    ('div', a, b)           a / b
    ('pow', a, b)           a ** b
    ('neg', a)              -a
    ('sin'|'cos'|'tan'|'exp'|'ln'|'sqrt', a)

sym_diff(expr) 可接受「字串」(會先剖析) 或「AST」，回傳化簡後的導函式 AST。

同時提供：
  - parse(str)      : 中序字串 -> AST (遞迴下降剖析器)
  - to_string(ast)  : AST -> 中序字串
  - evaluate(ast)   : 代入 x 求值
  - 數值驗證        : 與中央差分 (f(x+h)-f(x-h))/2h 比較
"""

import math

# ==================================================================
# 1. 運算子 / 前後順序
# ==================================================================
_PREC = {"add": 1, "sub": 1, "mul": 2, "div": 2, "neg": 3, "pow": 4}


def _prec(e):
    return _PREC.get(e[0], 99)   # 數字、變數、函式都當成「原子」


# ==================================================================
# 2. 剖析器：中序字串 -> AST
# ==================================================================
def tokenize(s):
    tokens = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or c == ".":
            j = i
            while j < n and (s[j].isdigit() or s[j] == "."):
                j += 1
            tokens.append(("num", float(s[i:j])))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < n and (s[j].isalnum() or s[j] == "_"):
                j += 1
            tokens.append(("name", s[i:j]))
            i = j
        elif s[i:i + 2] == "**":
            tokens.append(("op", "^"))
            i += 2
        elif c in "+-*/^()":
            tokens.append(("op", c))
            i += 1
        else:
            raise ValueError(f"無法辨識的字元: {c!r}")
    return tokens


class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def next(self):
        tok = self.toks[self.i]
        self.i += 1
        return tok

    def expect(self, op):
        kind, val = self.next()
        if kind != "op" or val != op:
            raise ValueError(f"預期 {op!r}，卻得到 {val!r}")

    # expr := term (('+'|'-') term)*
    def parse_expr(self):
        node = self.parse_term()
        while self.peek() == ("op", "+") or self.peek() == ("op", "-"):
            op = self.next()[1]
            rhs = self.parse_term()
            node = ("add" if op == "+" else "sub", node, rhs)
        return node

    # term := factor (('*'|'/') factor)*
    def parse_term(self):
        node = self.parse_factor()
        while self.peek() == ("op", "*") or self.peek() == ("op", "/"):
            op = self.next()[1]
            rhs = self.parse_factor()
            node = ("mul" if op == "*" else "div", node, rhs)
        return node

    # factor := unary ('^' factor)?          (^ 為右結合)
    def parse_factor(self):
        base = self.parse_unary()
        if self.peek() == ("op", "^"):
            self.next()
            exp = self.parse_factor()
            return ("pow", base, exp)
        return base

    # unary := '-' unary | primary
    def parse_unary(self):
        if self.peek() == ("op", "-"):
            self.next()
            return ("neg", self.parse_unary())
        if self.peek() == ("op", "+"):
            self.next()
            return self.parse_unary()
        return self.parse_primary()

    # primary := num | name | func '(' expr ')' | '(' expr ')'
    def parse_primary(self):
        kind, val = self.next()
        if kind == "num":
            return ("num", val)
        if kind == "name":
            if self.peek() == ("op", "("):     # 函式呼叫
                self.next()
                arg = self.parse_expr()
                self.expect(")")
                if val not in ("sin", "cos", "tan", "exp", "ln", "log", "sqrt"):
                    raise ValueError(f"未知函式: {val}")
                return ("ln" if val == "log" else val, arg)
            return ("var", val)
        if kind == "op" and val == "(":
            node = self.parse_expr()
            self.expect(")")
            return node
        raise ValueError(f"語法錯誤，讀到: {val!r}")


def parse(s):
    p = Parser(tokenize(s))
    node = p.parse_expr()
    if p.i != len(p.toks):
        raise ValueError("字串尾端有多餘內容")
    return node


# ==================================================================
# 3. 輸出：AST -> 中序字串 (視需要加括號)
# ==================================================================
_BIN_OP = {"add": "+", "sub": "-", "mul": "*", "div": "/", "pow": "^"}


def to_string(e):
    tag = e[0]
    if tag == "num":
        v = e[1]
        return str(int(v)) if v == int(v) else repr(v)
    if tag == "var":
        return e[1]
    if tag == "neg":
        inner = to_string(e[1])
        return f"-{_wrap(e[1], 3, False)}"
    if tag in ("sin", "cos", "tan", "exp", "ln", "sqrt"):
        return f"{tag}({to_string(e[1])})"
    if tag in _BIN_OP:
        p = _PREC[tag]
        left = _wrap(e[1], p, tag == "pow")                 # ^ 左邊同級要括號
        right = _wrap(e[2], p, tag in ("sub", "div"))       # - / 右邊同級要括號
        return f"{left} {_BIN_OP[tag]} {right}"
    raise ValueError(tag)


def _wrap(child, parent_prec, strict_equal):
    cp = _prec(child)
    need = cp < parent_prec or (cp == parent_prec and strict_equal)
    s = to_string(child)
    return f"({s})" if need else s


# ==================================================================
# 4. 化簡 (讓輸出的導函式乾淨一點)
# ==================================================================
def _is_num(e):
    return e[0] == "num"


def simplify(e):
    tag = e[0]
    if tag in ("num", "var"):
        return e
    if tag == "neg":
        a = simplify(e[1])
        if _is_num(a):
            return ("num", -a[1])
        if a[0] == "neg":
            return a[1]
        return ("neg", a)
    if tag in ("sin", "cos", "tan", "exp", "ln", "sqrt"):
        return (tag, simplify(e[1]))

    a, b = simplify(e[1]), simplify(e[2])
    an, bn = _is_num(a), _is_num(b)

    if tag == "add":
        if _is_num(a) and a[1] == 0:
            return b
        if _is_num(b) and b[1] == 0:
            return a
        if an and bn:
            return ("num", a[1] + b[1])
        return ("add", a, b)

    if tag == "sub":
        if _is_num(b) and b[1] == 0:
            return a
        if _is_num(a) and a[1] == 0:
            return simplify(("neg", b))
        if an and bn:
            return ("num", a[1] - b[1])
        return ("sub", a, b)

    if tag == "mul":
        if (an and a[1] == 0) or (bn and b[1] == 0):
            return ("num", 0.0)
        if an and a[1] == 1:
            return b
        if bn and b[1] == 1:
            return a
        if an and bn:
            return ("num", a[1] * b[1])
        return ("mul", a, b)

    if tag == "div":
        if an and a[1] == 0:
            return ("num", 0.0)
        if bn and b[1] == 1:
            return a
        if an and bn and b[1] != 0:
            return ("num", a[1] / b[1])
        return ("div", a, b)

    if tag == "pow":
        if bn and b[1] == 0:
            return ("num", 1.0)
        if bn and b[1] == 1:
            return a
        if an and bn:
            return ("num", a[1] ** b[1])
        return ("pow", a, b)

    raise ValueError(tag)


# ==================================================================
# 5. 微分核心 (全部靠遞迴)
# ==================================================================
def sym_diff(expr, var="x"):
    if isinstance(expr, str):
        expr = parse(expr)
    return simplify(_diff(expr, var))


def _diff(e, var):
    tag = e[0]

    if tag == "num":
        return ("num", 0.0)
    if tag == "var":
        return ("num", 1.0 if e[1] == var else 0.0)

    if tag == "add":
        return ("add", _diff(e[1], var), _diff(e[2], var))
    if tag == "sub":
        return ("sub", _diff(e[1], var), _diff(e[2], var))
    if tag == "neg":
        return ("neg", _diff(e[1], var))

    if tag == "mul":                                   # 乘法法則 (fg)' = f'g + fg'
        f, g = e[1], e[2]
        return ("add", ("mul", _diff(f, var), g), ("mul", f, _diff(g, var)))

    if tag == "div":                                   # 除法法則 (f/g)'
        f, g = e[1], e[2]
        num = ("sub", ("mul", _diff(f, var), g), ("mul", f, _diff(g, var)))
        return ("div", num, ("pow", g, ("num", 2.0)))

    if tag == "pow":
        base, exp = e[1], e[2]
        if exp[0] == "num":                            # 冪次法則 (f^n)' = n f^(n-1) f'
            n = exp[1]
            return ("mul", ("mul", ("num", n), ("pow", base, ("num", n - 1))),
                    _diff(base, var))
        # 一般式 f^g = e^(g ln f) 的推廣
        return ("mul", e, ("add",
                           ("mul", _diff(exp, var), ("ln", base)),
                           ("div", ("mul", exp, _diff(base, var)), base)))

    if tag == "sin":                                   # 連鎖法則
        return ("mul", ("cos", e[1]), _diff(e[1], var))
    if tag == "cos":
        return ("neg", ("mul", ("sin", e[1]), _diff(e[1], var)))
    if tag == "tan":
        return ("mul", ("div", ("num", 1.0), ("pow", ("cos", e[1]), ("num", 2.0))),
                _diff(e[1], var))
    if tag == "exp":
        return ("mul", ("exp", e[1]), _diff(e[1], var))
    if tag == "ln":
        return ("mul", ("div", ("num", 1.0), e[1]), _diff(e[1], var))
    if tag == "sqrt":
        return ("mul", ("div", ("num", 0.5), ("sqrt", e[1])), _diff(e[1], var))

    raise ValueError(f"無法微分的節點: {tag}")


# ==================================================================
# 6. 求值 + 數值驗證
# ==================================================================
def evaluate(e, env):
    tag = e[0]
    if tag == "num":
        return e[1]
    if tag == "var":
        return env[e[1]]
    if tag == "add":
        return evaluate(e[1], env) + evaluate(e[2], env)
    if tag == "sub":
        return evaluate(e[1], env) - evaluate(e[2], env)
    if tag == "mul":
        return evaluate(e[1], env) * evaluate(e[2], env)
    if tag == "div":
        return evaluate(e[1], env) / evaluate(e[2], env)
    if tag == "pow":
        return evaluate(e[1], env) ** evaluate(e[2], env)
    if tag == "neg":
        return -evaluate(e[1], env)
    if tag == "sin":
        return math.sin(evaluate(e[1], env))
    if tag == "cos":
        return math.cos(evaluate(e[1], env))
    if tag == "tan":
        return math.tan(evaluate(e[1], env))
    if tag == "exp":
        return math.exp(evaluate(e[1], env))
    if tag == "ln":
        return math.log(evaluate(e[1], env))
    if tag == "sqrt":
        return math.sqrt(evaluate(e[1], env))
    raise ValueError(tag)


def numeric_check(expr, d_expr, x0, h=1e-6):
    """中央差分逼近導數，和符號微分結果比較。"""
    f_plus = evaluate(expr, {"x": x0 + h})
    f_minus = evaluate(expr, {"x": x0 - h})
    approx = (f_plus - f_minus) / (2 * h)
    exact = evaluate(d_expr, {"x": x0})
    return approx, exact, abs(approx - exact)


# ==================================================================
# 7. 主程式
# ==================================================================
def main():
    print("=" * 70)
    print("符號微分 sym_diff(expr)")
    print("=" * 70)

    cases = [
        "3*x^2 + 2*x - 5",
        "x^3 - 4*x^2 + 7*x - 1",
        "sin(x)*cos(x)",
        "x^2 * sin(x)",
        "sin(x^2)",
        "exp(x) / (1 + x^2)",
        "ln(x^2 + 1)",
        "tan(x)",
        "sqrt(1 + x^2)",
        "x^x",
    ]

    for s in cases:
        expr = parse(s)
        d = sym_diff(expr)
        print(f"\nf(x)  = {to_string(expr)}")
        print(f"f'(x) = {to_string(d)}")
        approx, exact, err = numeric_check(expr, d, 0.7)
        print(f"  驗證 x=0.7: 符號={exact:.10f}  數值={approx:.10f}  誤差={err:.2e}")

    print("\n" + "=" * 70)
    print("二階導數 (對 f'(x) 再微分一次)")
    print("=" * 70)
    expr = parse("x^3 * sin(x)")
    d1 = sym_diff(expr)
    d2 = sym_diff(d1)
    print(f"f   = {to_string(expr)}")
    print(f"f'  = {to_string(d1)}")
    print(f"f'' = {to_string(d2)}")


if __name__ == "__main__":
    main()
