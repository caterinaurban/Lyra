
x: int = 2
# STATE: x -> [2, 2]
if x in range(0):
    # STATE: x -> ⊥
    print(x)
else:
    raise ValueError
# FINAL: x -> ⊥
