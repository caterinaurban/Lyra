
a: int = int(input())
# STATE: a -> >0
a: int = a - 1
# STATE: a -> ≥0
if a < 0:
    # STATE: a -> ⊥
    raise ValueError
