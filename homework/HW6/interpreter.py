#!/usr/bin/env python3
"""
Lambda Calculus Interpreter (named version)
- Shows complete beta-reduction steps with normal order
- Supports \\x.M, M N, (M), variables
"""

from lambda_calculus import Parser, NamedEvaluator, Term, Var, Abs, App


class LambdaInterpreter:
    def __init__(self, max_steps=50):
        self.parser = Parser()
        self.max_steps = max_steps

    def evaluate(self, expr: str, show_steps=True) -> Term:
        ev = NamedEvaluator(show_steps=show_steps, max_steps=self.max_steps)
        return ev.eval_from_string(expr)

    def format_term(self, t: Term) -> str:
        return str(t)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py \"(\\x.x)(\\y.y)\"")
        print("Or run without args for demo")
        print("\n=== Demo ===")
        from sample_programs import SAMPLE_PROGRAMS
        ev = NamedEvaluator(show_steps=True)
        ev.eval_from_string(SAMPLE_PROGRAMS['example1'])
        sys.exit(0)
    expr = ' '.join(sys.argv[1:]) if len(sys.argv) > 2 else sys.argv[1]
    ev = NamedEvaluator(show_steps=True)
    ev.eval_from_string(expr)
