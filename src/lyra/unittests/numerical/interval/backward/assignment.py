
a: int = int(input())
# STATE: a -> [-inf, 10]
a: int = a - 1
# STATE: a -> [-inf, 9]
if a > 9:
    # STATE: a -> ⊥
    raise ValueError
