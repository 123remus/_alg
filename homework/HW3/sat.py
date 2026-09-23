"""
HW3 : 系統性列舉真值表，暴力解決 SAT 問題

SAT (Boolean Satisfiability Problem) :
    給定一個布林公式，問是否存在一組「變數指派」(每個變數給 True/False)
    讓整個公式的結果為 True。
    存在      => SATISFIABLE  (可滿足，並輸出所有可行指派)
    不存在    => UNSATISFIABLE (不可滿足)

本程式的方法 (暴力列舉真值表)：
    1. 把公式 parse 成語法樹 (AST)
    2. 找出公式裡出現的所有變數 (n 個)
    3. 系統性地列出 2^n 種指派，湊出一張完整的真值表
    4. 每一列代入公式求值，只要有一列算出來是 True 就找到解

這是「試遍所有可能」最直接也最暴力演算法：保證正確、易懂，
代價是時間 O(2^n)，變數 n 稍微變大就會指數爆炸（這就是 SAT 是 NP 問題的原因）。

另外附贈兩種進階做法一起比較（證明暴力列舉只是基準線）：
    - 從真值表反向生成等價的 CNF / DNF 表示式
    - DPLL 演算法 (單元傳播 + 回溯)，大幅縮小搜尋空間

支援的運算子 (由低到高優先權)：
    ->    實質蘊含 (implies)           a -> b  等價於  not a or b
    or    邏輯或        ( |  ||  or )
    xor   互斥或        ( ^  xor )
    and   邏輯且        ( &  &&  and )
    not   邏輯非        ( !  not )
    ()    括號
    常數  true / false / 1 / 0
"""

import random
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

# ------------------------------------------------------------
# 詞法分析 : 把字串切成 token 串
# ------------------------------------------------------------
TOKEN_RE = re.compile(r"""
    \s*(?:
        (?P<name>[A-Za-z_][A-Za-z0-9_]*)
      | (?P<num>[01]\b)
      | (?P<not>!)
      | (?P<and>&&|&)
      | (?P<or>\|\||\|)
      | (?P<xor>\^)
      | (?P<impl>->|=>)
      | (?P<lp>\()
      | (?P<rp>\))
    )
""", re.VERBOSE)

_KEYWORDS = {
    "not": "not", "and": "and", "or": "or",
    "xor": "xor", "implies": "impl", "if": None,
    "true": "true", "false": "false",
}


def tokenize(src: str) -> List[Tuple[str, object]]:
    tokens = []
    i = 0
    while i < len(src):
        m = TOKEN_RE.match(src, i)
        if not m:
            raise ValueError(f"無法解析的字元: {src[i]!r}")
        i = m.end()
        kind = m.lastgroup
        if kind == "name":
            low = m.group("name").lower()
            if low in _KEYWORDS:
                mapped = _KEYWORDS[low]
                if mapped == "true":
                    tokens.append(("num", True))
                elif mapped == "false":
                    tokens.append(("num", False))
                else:
                    tokens.append((mapped, None))
            else:
                tokens.append(("name", m.group("name")))
        elif kind == "num":
            tokens.append(("num", m.group("num") == "1"))
        elif kind in ("not", "and", "or", "xor", "impl", "lp", "rp"):
            tokens.append((kind, None))
    tokens.append(("end", None))
    return tokens


# ------------------------------------------------------------
# 語法分析 : 遞迴下降，建出 AST
#   節點格式 (kind, ...)：
#     ("var", 名稱)  ("true",)  ("false",)
#     ("not", e)
#     ("and", l, r)  ("or", l, r)  ("xor", l, r)  ("impl", l, r)
# ------------------------------------------------------------
class Parser:
    def __init__(self, tokens: List[Tuple[str, object]]):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos][0]

    def advance(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def expr(self):
        return self.impl()

    def impl(self):                       # ->  最低優先權，右結合
        left = self.or_()
        if self.peek() == "impl":
            self.advance()
            right = self.impl()
            return ("impl", left, right)
        return left

    def or_(self):                        # or
        left = self.xor_()
        while self.peek() == "or":
            self.advance()
            right = self.xor_()
            left = ("or", left, right)
        return left

    def xor_(self):                       # xor
        left = self.and_()
        while self.peek() == "xor":
            self.advance()
            right = self.and_()
            left = ("xor", left, right)
        return left

    def and_(self):                       # and
        left = self.unary()
        while self.peek() == "and":
            self.advance()
            right = self.unary()
            left = ("and", left, right)
        return left

    def unary(self):                      # not
        if self.peek() == "not":
            self.advance()
            return ("not", self.unary())
        return self.primary()

    def primary(self):                    # 變數 / 常數 / (公式)
        tok = self.tokens[self.pos]
        if tok[0] == "name":
            self.advance()
            return ("var", tok[1])
        if tok[0] == "num":
            self.advance()
            return ("true",) if tok[1] else ("false",)
        if tok[0] == "lp":
            self.advance()
            e = self.expr()
            if self.peek() != "rp":
                raise ValueError("少了右括號 )")
            self.advance()
            return e
        raise ValueError(f"意外的 token: {tok}")


def parse(src: str):
    return Parser(tokenize(src)).expr()


# ------------------------------------------------------------
# 求值 : 給定一組指派，算出語法樹的值
# ------------------------------------------------------------
def evaluate(node, assign: Dict[str, bool]) -> bool:
    k = node[0]
    if k == "var":
        return assign[node[1]]
    if k == "true":
        return True
    if k == "false":
        return False
    if k == "not":
        return not evaluate(node[1], assign)
    if k == "and":
        return evaluate(node[1], assign) and evaluate(node[2], assign)
    if k == "or":
        return evaluate(node[1], assign) or evaluate(node[2], assign)
    if k == "xor":
        return evaluate(node[1], assign) != evaluate(node[2], assign)
    if k == "impl":
        return (not evaluate(node[1], assign)) or evaluate(node[2], assign)
    raise ValueError(f"未知節點: {node}")


# ------------------------------------------------------------
# 收集變數 (照出現順序，去重)
# ------------------------------------------------------------
def collect_vars(node, seen=None, out=None) -> List[str]:
    if seen is None:
        seen, out = set(), []
    k = node[0]
    if k == "var":
        if node[1] not in seen:
            seen.add(node[1])
            out.append(node[1])
    elif k in ("and", "or", "xor", "impl"):
        collect_vars(node[1], seen, out)
        collect_vars(node[2], seen, out)
    elif k == "not":
        collect_vars(node[1], seen, out)
    return out


# ------------------------------------------------------------
# 系統性列舉真值表 : 2^n 種指派
#   mask 從 0 數到 2^n - 1，第 i 個 bit 就是第 i 個變數的值
# ------------------------------------------------------------
def enumerate_assignments(vars_: List[str]):
    n = len(vars_)
    for mask in range(1 << n):
        assign = {v: bool((mask >> i) & 1) for i, v in enumerate(vars_)}
        yield mask, assign


def build_truth_table(node, vars_: List[str]):
    """一張完整真值表，每列是 (mask, 指派, 結果)"""
    return [(mask, assign, evaluate(node, assign))
            for mask, assign in enumerate_assignments(vars_)]


# ------------------------------------------------------------
# SAT 求解器 (暴力列舉)
# ------------------------------------------------------------
def solve_sat(node, vars_: List[str]):
    """回傳 (是否可行, 所有可行指派列表, 完整真值表)"""
    table = build_truth_table(node, vars_)
    models = [(mask, assign) for mask, assign, val in table if val]
    return (len(models) > 0), models, table


# ------------------------------------------------------------
# 從真值表反向產生等價 CNF / DNF
#   子句/項的元素是 literal : ("v", 名稱) 正 / ("n", 名稱) 負
# ------------------------------------------------------------
def build_cnf(vars_: List[str], table) -> List[List[Tuple[str, str]]]:
    """每個結果為 False 的列，生一個子句 (OR)，保證該列被推翻。"""
    clauses = []
    for _mask, assign, val in table:
        if val:
            continue
        clauses.append([("n", v) if assign[v] else ("v", v) for v in vars_])
    return clauses


def build_dnf(vars_: List[str], table) -> List[List[Tuple[str, str]]]:
    """每個結果為 True 的列，生一個項 (AND)，保證該列被命中。"""
    terms = []
    for _mask, assign, val in table:
        if not val:
            continue
        terms.append([("v", v) if assign[v] else ("n", v) for v in vars_])
    return terms


# ------------------------------------------------------------
# DPLL 加速 : 單元傳播 + 回溯 (需要 CNF 輸入)
# ------------------------------------------------------------
def lit_value(lit, assign: Dict[str, bool]):
    """回傳該 literal 目前的值；尚未指派回傳 None。"""
    name = lit[1]
    if name not in assign:
        return None
    val = assign[name]
    return val if lit[0] == "v" else (not val)


def simplify_cnf(clauses, assign: Dict[str, bool]):
    """把已賦值的變數代入 CNF；回傳新子句串，衝突就回傳 None。"""
    new_clauses = []
    for cl in clauses:
        remaining = []
        sat = False
        for lit in cl:
            val = lit_value(lit, assign)
            if val is True:
                sat = True
                break
            if val is None:
                remaining.append(lit)
        if sat:
            continue
        if not remaining:
            return None          # 這個子句整條是 False => 衝突
        new_clauses.append(remaining)
    return new_clauses


def dpll(clauses, vars_: List[str], assign: Dict[str, bool],
         stats: Dict[str, int]) -> Optional[Dict[str, bool]]:
    """回朔搜尋；找到解回傳完整指派，找不到回傳 None。"""
    cs = simplify_cnf(clauses, assign)
    if cs is None:
        stats["conflicts"] += 1
        return None

    # 單元傳播 : 只要出現長度 1 的子句就立刻照它指派，並重新簡化
    changed = True
    while changed:
        changed = False
        for cl in cs:
            if len(cl) == 1:
                lit = cl[0]
                name = lit[1]
                cur = lit_value(lit, assign)
                if cur is False:
                    stats["conflicts"] += 1
                    return None
                if cur is None:
                    assign[name] = (lit[0] == "v")
                    stats["decisions"] += 1
                    changed = True
                    break
        if changed:
            cs = simplify_cnf(clauses, assign)
            if cs is None:
                stats["conflicts"] += 1
                return None

    if not cs:
        return _complete(assign, vars_)          # 所有子句都被滿足 => 找到解

    # 選一個未指派變數做分支 (回溯)
    for name in vars_:
        if name not in assign:
            for val in (True, False):
                stats["decisions"] += 1
                branch = dict(assign)
                branch[name] = val
                result = dpll(cs, vars_, branch, stats)
                if result is not None:
                    return result
            return None
    return _complete(assign, vars_)


def _complete(assign: Dict[str, bool], vars_: List[str]) -> Dict[str, bool]:
    """把還沒指派的變數補成 False，讓回傳的指派是「完整」的。"""
    return {v: assign.get(v, False) for v in vars_}


# ------------------------------------------------------------
# 輸出工具
# ------------------------------------------------------------
def fmt_assign(vars_: List[str], assign: Dict[str, bool]) -> str:
    return "  ".join(("T" if assign[v] else "F") for v in vars_)


def lit_str(lit) -> str:
    return ("~" if lit[0] == "n" else "") + lit[1]


def cnf_str(clauses) -> str:
    if not clauses:
        return "⊤ (永真，空 CNF)"
    return " & ".join("(" + " | ".join(lit_str(l) for l in cl) + ")"
                      for cl in clauses)


def dnf_str(terms) -> str:
    if not terms:
        return "⊥ (永假，空 DNF)"
    return " | ".join("(" + " & ".join(lit_str(l) for l in t) + ")"
                      for t in terms)


def expr_str(node) -> str:
    """把 AST 印回成可讀的字串。"""
    k = node[0]
    if k == "var":
        return node[1]
    if k == "true":
        return "true"
    if k == "false":
        return "false"
    if k == "not":
        return "not " + expr_str(node[1])
    sym = {"and": " and ", "or": " or ", "xor": " xor ", "impl": " -> "}[k]
    return "(" + expr_str(node[1]) + sym + expr_str(node[2]) + ")"


# ------------------------------------------------------------
# 範例 1 : 先看一個有解的公式，印出整張真值表
# ------------------------------------------------------------
def demo_truth_table(node, vars_: List[str]):
    print("  " + "   ".join(vars_) + "   結果")
    print("  " + "-" * (4 * len(vars_) + 5))
    sat, models, table = solve_sat(node, vars_)
    for mask, assign, val in table:
        mark = "  <== 找到解" if val else ""
        print(f"  {fmt_assign(vars_, assign)}   {'T' if val else 'F'}{mark}")
    print(f"\n  => {len(vars_)} 個變數，共列出 2^{len(vars_)} = {1 << len(vars_)} 列指派")
    print(f"  => 有 {len(models)} 列結果為 True  =>  {'SATISFIABLE (可滿足)' if sat else 'UNSATISFIABLE (不可滿足)'}")
    if models:
        for mask, assign in models:
            print(f"      可行指派 : {fmt_assign(vars_, assign)}  (bit {mask:0{len(vars_)}b})")


# ------------------------------------------------------------
# 範例 2 : 同一公式用 CNF / DNF 重新表示
# ------------------------------------------------------------
def demo_cnf_dnf(node, vars_: List[str]):
    table = build_truth_table(node, vars_)
    clauses = build_cnf(vars_, table)
    terms = build_dnf(vars_, table)
    print("  (a) 等價 CNF (由所有 False 列生成):")
    print("       " + cnf_str(clauses))
    print("  (b) 等價 DNF (由所有 True 列生成):")
    print("       " + dnf_str(terms))


# ------------------------------------------------------------
# 範例 3 : DPLL 對同一公式求解
# ------------------------------------------------------------
def demo_dpll(node, vars_: List[str]):
    table = build_truth_table(node, vars_)
    clauses = build_cnf(vars_, table)
    stats = {"decisions": 0, "conflicts": 0}
    assign = {}
    t0 = time.perf_counter()
    sol = dpll(clauses, vars_, assign, stats)
    dt = time.perf_counter() - t0
    if sol is None:
        print(f"  => DPLL : UNSATISFIABLE (反證完畢)  走訪 {stats['decisions']} 個節點, 衝突 {stats['conflicts']} 次, {dt*1000:.3f} ms")
    else:
        print(f"  => DPLL : SATISFIABLE  找到指派 {fmt_assign(vars_, sol)}  走訪 {stats['decisions']} 個節點, 衝突 {stats['conflicts']} 次, {dt*1000:.3f} ms")
    print(f"     暴力列舉則需全部 2^{len(vars_)} = {1 << len(vars_)} 列才敢斷言")


# ------------------------------------------------------------
# 範例 4 : 隨機 3-SAT，比較「暴力列舉」與「DPLL」
# ------------------------------------------------------------
def random_sat(n_vars: int, n_clauses: int, seed: int):
    """製造一個保證有解的隨機 3-SAT：先偷偷選一個 model，再生成都被它滿足的子句。"""
    rnd = random.Random(seed)
    vars_ = [f"x{i}" for i in range(n_vars)]
    model = {v: bool(rnd.getrandbits(1)) for v in vars_}
    clauses = []
    for _ in range(n_clauses):
        chosen = rnd.sample(vars_, 3)
        cl = []
        for v in chosen:
            cl.append(("v", v) if model[v] else ("n", v))
        clauses.append(cl)
    return vars_, clauses


def demo_random_3sat():
    n_vars, n_clauses = 16, 24
    print(f"  隨機 3-SAT : {n_vars} 個變數, {n_clauses} 條子句 (保證有解)")
    vars_, clauses = random_sat(n_vars, n_clauses, seed=888)

    # 方法 A : 暴力列舉真值表 (所有 2^n 列都得算)
    table_rows = 1 << n_vars
    t0 = time.perf_counter()
    enum_sat = False
    for mask in range(table_rows):
        assign = {}
        for i, v in enumerate(vars_):
            assign[v] = bool((mask >> i) & 1)
        if all(any(lit_value(l, assign) for l in cl) for cl in clauses):
            enum_sat = True
            break
    enum_dt = time.perf_counter() - t0
    print(f"  [暴力列舉] 檢查到第 {mask + 1} 列就找到解, "
          f"最壞需看 2^{n_vars} = {table_rows:,} 列, 花 {enum_dt*1000:.3f} ms")

    # 方法 B : DPLL
    stats = {"decisions": 0, "conflicts": 0}
    t0 = time.perf_counter()
    sol = dpll(clauses, vars_, {}, stats)
    dpll_dt = time.perf_counter() - t0
    print(f"  [DPLL     ] 走訪 {stats['decisions']} 節點 (遠小於 {table_rows:,}), "
          f"衝突 {stats['conflicts']} 次, 花 {dpll_dt*1000:.3f} ms")
    print(f"  兩者結果一致 : {enum_sat == (sol is not None)}  (暴力={enum_sat}, DPLL={'SAT' if sol else 'UNSAT'})")

    # 驗證 DPLL 找到的解真的讓所有子句為真
    if sol:
        ok = all(any(lit_value(l, sol) for l in cl) for cl in clauses)
        print(f"  驗證 DPLL 的指派真正滿足全部 {n_clauses} 條子句 : {ok}")


# ------------------------------------------------------------
# 主流程
# ------------------------------------------------------------
def run_example(title, formula_str):
    print("=" * 70)
    print(f"範例 : {title}")
    print("  公式 : " + formula_str)
    node = parse(formula_str)
    vars_ = collect_vars(node)
    print(f"  語法樹 : {expr_str(node)}")
    print(f"  變數有 {len(vars_)} 個 : {', '.join(vars_)}")
    print()
    demo_truth_table(node, vars_)
    print("\n  從真值表反向生成的等價表示式：")
    demo_cnf_dnf(node, vars_)
    print("\n  改用 DPLL 比較看看：")
    demo_dpll(node, vars_)
    print()


def main():
    print(f"SAT 暴力求解器 (系統性列舉真值表)   Python {'.'.join(map(str, sys.version_info[:3]))}")
    print()

    # 若命令列有帶公式，直接解那一條
    if len(sys.argv) >= 2:
        formula = " ".join(sys.argv[1:])
        run_example("命令列輸入", formula)
        return

    run_example("有解公式 (3 個變數)", "(a or b) and (not a or c) and (b or not c)")
    run_example("無解公式 (矛盾)", "a and b and (not a or not b)")
    run_example("恆真公式 (必然式)", "(a and b) or not a or not b")
    run_example("蘊含與互斥或", "a xor b  implies  (a or b)")

    print("=" * 70)
    print("暴力列舉 vs DPLL ：誰比較快？")
    print("=" * 70)
    demo_random_3sat()
    print()
    print("=" * 70)
    print("結論")
    print("=" * 70)
    print("  暴力列舉真值表 : 保證正確，但要看完 2^n 列，O(2^n) 指數爆炸。")
    print("  所以 SAT 被歸類為 NP 問題，n 到 30 以上就很難這樣硬算。")
    print("  不過對小 n 來說，列真值表是最簡單、最不容易出錯的方法。")
    print("  進階做法 (DPLL、回溯、單元傳播、CDCL...) 本質上也是在搜尋")
    print("  同一張真值表，只是用聰明的剪枝跳過大量顯然會失敗的列。")

    # 最後用一個隱藏公式自我測試：列舉解 必定等於 DPLL 解
    formulas = [
        "(a or b) and (not a or c) and (b or not c)",
        "a and b and (not a or not b)",
        "(a and b) or not a or not b",
        "a xor b implies (a or b)",
        "(p or q or r) and (not p or not q) and (r or not p)",
    ]
    all_ok = True
    for f in formulas:
        node = parse(f)
        vars_ = collect_vars(node)
        table = build_truth_table(node, vars_)
        clauses = build_cnf(vars_, table)
        enum_sat = any(v for _m, _a, v in table)
        sol = dpll(clauses, vars_, {}, {"decisions": 0, "conflicts": 0})
        same = (enum_sat == (sol is not None))
        all_ok = all_ok and same
        print(f"  自我測試 [{f:>60}] 列舉={enum_sat}  DPLL={sol is not None}  一致={same}")
    print(f"  全部一致 : {all_ok}")


if __name__ == "__main__":
    main()