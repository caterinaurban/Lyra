
x: int = -9
# STATE: x -> [-9, -9]
if x in range(int(input())):
    # STATE: x -> ⊥
    print(x)
else:
    raise ValueError
# FINAL: x -> ⊥
