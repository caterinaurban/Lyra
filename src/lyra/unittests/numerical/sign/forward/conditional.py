# INITIAL: a -> ⊤, b -> ⊤
a: int = int(input())
# STATE: a -> ⊤, b -> ⊤
if 1 <= a <= 9:
    # STATE: a -> >0, b -> ⊤
    b: int = 0
    # STATE: a -> >0, b -> =0
else:
    # STATE: a -> ⊤, b -> ⊤
    b: int = 2
    # STATE: a -> ⊤, b -> >0
# FINAL: a -> ⊤, b -> ≥0
