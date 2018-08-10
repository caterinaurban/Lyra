# INITIAL: a -> ⊤
a: int = 10
# STATE: a -> >0
while a > 0:
    # STATE: a -> >0
    a = a - 1
    # STATE: a -> ⊤
# FINAL: a -> ≤0
