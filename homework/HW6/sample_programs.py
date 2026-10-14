"""
Sample Lambda Calculus programs for testing the interpreter.
"""

# Common combinators
SAMPLE_PROGRAMS = {
    "identity": r"(\x.x)",
    "I": r"(\x.x)",
    "K": r"(\x.\y.x)",  # true
    "true": r"(\x.\y.x)",
    "K2": r"(\x.\y.y)",  # false
    "false": r"(\x.\y.y)",
    "S": r"(\f.\g.\x.f x (g x))",
    "omega": r"(\x.x x)(\x.x x)",
    "Y": r"(\f.(\x.f (x x)) (\x.f (x x)))",
    
    # Application
    "apply": r"(\x.\y.x y)",
    "self_apply": r"(\x.x x)",
    
    # Boolean logic
    "not": r"(\b.b (\x.\y.y) (\x.\y.x))",
    "and": r"(\p.\q.p q p)",
    "or": r"(\p.\q.p p q)",
    
    # Church numerals (small examples)
    "zero": r"(\f.\x.x)",
    "one": r"(\f.\x.f x)",
    "two": r"(\f.\x.f (f x))",
    "three": r"(\f.\x.f (f (f x)))",
    "succ": r"(\n.\f.\x.f (n f x))",
    "plus": r"(\m.\n.\f.\x.m f (n f x))",
    
    # Pairs
    "pair": r"(\x.\y.\f.f x y)",
    "fst": r"(\p.p (\x.\y.x))",
    "snd": r"(\p.p (\x.\y.y))",
    
    # Examples showing reduction
    "example1": r"(\x.\y.x y)(\z.z)",  # should reduce to identity
    "example2": r"(\x.x)(\y.y)(\z.z)",
    "example3": r"(\x.\y.x)(\a.a)(\b.b b)",
    "example4": r"(\f.\x.f (f x))(\y.y)",
}

# Descriptions
DESCRIPTIONS = {
    "identity": "Identity function",
    "K": "True combinator",
    "false": "False combinator", 
    "omega": "Divergent term (ω ω)",
    "Y": "Y combinator (fixed point)",
    "not": "Boolean NOT",
    "and": "Boolean AND",
    "or": "Boolean OR",
    "succ": "Successor on Church numerals",
    "plus": "Addition of Church numerals",
    "example1": "Simple application reducing to identity",
}
