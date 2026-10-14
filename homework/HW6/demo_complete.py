#!/usr/bin/env python3
from lambda_calculus import NamedEvaluator, DeBruijnConverter, Parser
from sample_programs import SAMPLE_PROGRAMS

def main():
    print("=== Lambda Calculus Interpreter Demo ===\n")
    print("1. Named version examples:\n")
    
    examples = [
        SAMPLE_PROGRAMS['example1'],
        SAMPLE_PROGRAMS['example2'],
        SAMPLE_PROGRAMS['example3'],
        SAMPLE_PROGRAMS['SKK'] if 'SKK' in SAMPLE_PROGRAMS else r"(\f.\g.\x.f x (g x))(\x.\y.x)(\x.\y.x)",
    ]
    for i, ex in enumerate(examples, 1):
        print(f"--- Example {i}: {ex} ---")
        ev = NamedEvaluator(show_steps=True, max_steps=40)
        ev.eval_from_string(ex)
        print()
    
    print("2. De Bruijn conversion (name-free representation):\n")
    p = Parser()
    t = p.parse(SAMPLE_PROGRAMS['example1'])
    db = DeBruijnConverter.to_debruijn(t)
    print(f"Named: {t}")
    print(f"De Bruijn: {db}\n")
    
    print("3. Boolean logic example - NOT FALSE:\n")
    not_false = r"(\b.b (\x.\y.y) (\x.\y.x))(\x.\y.y)"
    print(f"Expression: {not_false}")
    ev = NamedEvaluator(show_steps=True, max_steps=30)
    ev.eval_from_string(not_false)
    print()
    
    print("=== Demo Complete ===")

if __name__ == "__main__":
    main()
