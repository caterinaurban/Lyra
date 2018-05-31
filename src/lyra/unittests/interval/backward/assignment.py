
a: int = int(input())
# RESULT: a -> [-oo, 10]
a : int = a - 1
# RESULT: a -> [-oo, 9]
if a > 9:
    # RESULT: a -> ⊥
    raise ValueError
