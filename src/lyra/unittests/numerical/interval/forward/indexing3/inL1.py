
L: List[int] = list()
x: int = -9
# STATE: L -> _@⊥; len(L) -> [0, 0]; x -> [-9, -9]
if x in L:
    # STATE: L -> _@⊥; len(L) -> [0, 0]; x -> ⊥
    print(x)
else:
    raise ValueError
# FINAL: L -> _@⊥; len(L) -> [0, 0]; x -> ⊥
