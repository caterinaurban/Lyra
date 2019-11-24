
# STATE: x -> ⊥
x: int = 9
# STATE: x -> [1, 5]
if x < 1 or 5 < x:
    raise ValueError
