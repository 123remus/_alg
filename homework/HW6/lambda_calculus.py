#!/usr/bin/env python3
"""
Complete Lambda Calculus Interpreter with step-by-step traces
"""

import re
from dataclasses import dataclass
from typing import List, Union, Tuple


@dataclass(eq=False)
class Var:
    name: str
    def __str__(self): return self.name
    def __repr__(self): return f"Var({self.name})"


@dataclass(eq=False)
class Abs:
    var: str
    body: 'Term'
    def __str__(self): return f"(\\{self.var}.{self.body})"
    def __repr__(self): return f"Abs({self.var},{self.body})"


@dataclass(eq=False)
class App:
    left: 'Term'
    right: 'Term'
    def __str__(self): return f"({self.left} {self.right})"
    def __repr__(self): return f"App({self.left},{self.right})"


Term = Union[Var, Abs, App]


class Parser:
    def __init__(self):
        self.tokens = []
        self.pos = 0

    def tokenize(self, s: str):
        s = s.replace('λ', '\\')
        token_re = re.compile(r'\\|\.|\(|\)|[a-zA-Z_][a-zA-Z0-9_]*|\s+')
        self.tokens = []
        for m in token_re.finditer(s):
            t = m.group(0)
            if t.strip():
                self.tokens.append(t.strip())
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected=None):
        t = self.current()
        if expected is not None and t != expected:
            raise SyntaxError(f"Expected {expected}, got {t}")
        self.pos += 1
        return t

    def parse(self, s: str) -> Term:
        self.tokenize(s)
        return self.parse_expr()

    def parse_expr(self) -> Term:
        return self.parse_app()

    def parse_app(self) -> Term:
        t = self.parse_atom()
        while self.current() is not None and self.current() != ')':
            t = App(t, self.parse_atom())
        return t

    def parse_atom(self) -> Term:
        tok = self.current()
        if tok is None:
            raise SyntaxError("Unexpected EOF")
        if tok == '(':
            self.eat('(')
            t = self.parse_expr()
            self.eat(')')
            return t
        if tok == '\\':
            self.eat('\\')
            v = self.eat()
            if self.current() == '.':
                self.eat('.')
            body = self.parse_expr()
            return Abs(v, body)
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', tok):
            self.eat(tok)
            return Var(tok)
        raise SyntaxError(f"Unexpected token: {tok}")


class NamedEvaluator:
    def __init__(self, show_steps=True, max_steps=50):
        self.show_steps = show_steps
        self.max_steps = max_steps
        self.step = 0

    def free_vars(self, term):
        if isinstance(term, Var):
            return {term.name}
        elif isinstance(term, Abs):
            return self.free_vars(term.body) - {term.var}
        elif isinstance(term, App):
            return self.free_vars(term.left) | self.free_vars(term.right)
        return set()

    def fresh_var(self, name, used):
        if name not in used:
            return name
        i = 0
        while f"{name}{i}" in used:
            i += 1
        return f"{name}{i}"

    def clone(self, term):
        if isinstance(term, Var):
            return Var(term.name)
        elif isinstance(term, Abs):
            return Abs(term.var, self.clone(term.body))
        elif isinstance(term, App):
            return App(self.clone(term.left), self.clone(term.right))

    def substitute(self, term, var, repl, used=None):
        if used is None:
            used = self.free_vars(term) | self.free_vars(repl) | {var}
        if isinstance(term, Var):
            if term.name == var:
                return self.clone(repl)
            return term
        elif isinstance(term, Abs):
            if term.var == var:
                return term
            if term.var in self.free_vars(repl):
                nv = self.fresh_var(term.var, used | {term.var})
                used.add(nv)
                nb = self.substitute(term.body, term.var, Var(nv), used)
                nb = self.substitute(nb, var, repl, used)
                return Abs(nv, nb)
            else:
                nb = self.substitute(term.body, var, repl, used)
                return Abs(term.var, nb)
        elif isinstance(term, App):
            return App(self.substitute(term.left, var, repl, used),
                       self.substitute(term.right, var, repl, used))
        return term

    def is_redex(self, t):
        return isinstance(t, App) and isinstance(t.left, Abs)

    def beta_reduce(self, term):
        if isinstance(term, Var):
            return term, False
        elif isinstance(term, Abs):
            b, red = self.beta_reduce(term.body)
            if red:
                return Abs(term.var, b), True
            return term, False
        elif isinstance(term, App):
            if self.is_redex(term):
                abs_t = term.left  # Abs
                res = self.substitute(abs_t.body, abs_t.var, term.right)
                return res, True
            # reduce leftmost outermost - try left first
            l, redl = self.beta_reduce(term.left)
            if redl:
                return App(l, term.right), True
            r, redr = self.beta_reduce(term.right)
            if redr:
                return App(term.left, r), True
            return term, False
        return term, False

    def eval(self, term):
        cur = self.clone(term)
        if self.show_steps:
            print(f"Initial: {cur}")
        while self.step < self.max_steps:
            self.step += 1
            nxt, red = self.beta_reduce(cur)
            if not red:
                if self.show_steps:
                    print(f"Normal form reached ({self.step - 1} steps)")
                    print(f"Result: {nxt}")
                return nxt
            cur = nxt
            if self.show_steps:
                print(f"Step {self.step}: {cur}")
        if self.show_steps:
            print(f"Stopped after {self.max_steps} steps (max)")
            print(f"Result: {cur}")
        return cur

    def eval_from_string(self, s: str):
        p = Parser()
        t = p.parse(s)
        return self.eval(t)


# ========== De Bruijn Index Support ==========

@dataclass(eq=False)
class DBVar:
    index: int
    def __str__(self): return str(self.index)
    def __repr__(self): return f"DBVar({self.index})"


@dataclass(eq=False)
class DBAbs:
    body: 'DBTerm'
    def __str__(self): return f"(\\. {self.body})"
    def __repr__(self): return f"DBAbs({self.body})"


@dataclass(eq=False)
class DBApp:
    left: 'DBTerm'
    right: 'DBTerm'
    def __str__(self): return f"({self.left} {self.right})"
    def __repr__(self): return f"DBApp({self.left},{self.right})"


DBTerm = Union[DBVar, DBAbs, DBApp]


class DeBruijnConverter:
    @staticmethod
    def to_debruijn(term: Term, ctx: List[str] = None) -> DBTerm:
        if ctx is None:
            ctx = []
        if isinstance(term, Var):
            try:
                idx = ctx.index(term.name) + 1
                return DBVar(idx)
            except ValueError:
                return DBVar(len(ctx) + 500)
        elif isinstance(term, Abs):
            new_ctx = [term.var] + ctx
            return DBAbs(DeBruijnConverter.to_debruijn(term.body, new_ctx))
        elif isinstance(term, App):
            return DBApp(
                DeBruijnConverter.to_debruijn(term.left, ctx),
                DeBruijnConverter.to_debruijn(term.right, ctx)
            )

    @staticmethod
    def from_debruijn(term: DBTerm, ctx: List[str] = None) -> Term:
        if ctx is None:
            ctx = []
        if isinstance(term, DBVar):
            idx = term.index
            if 1 <= idx <= len(ctx):
                return Var(ctx[idx - 1])
            return Var(f"v{idx}")
        elif isinstance(term, DBAbs):
            body = DeBruijnConverter.from_debruijn(term.body, ["x"] + ctx)
            return Abs("x", body)
        elif isinstance(term, DBApp):
            return App(
                DeBruijnConverter.from_debruijn(term.left, ctx),
                DeBruijnConverter.from_debruijn(term.right, ctx)
            )
