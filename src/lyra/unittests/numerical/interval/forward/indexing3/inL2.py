
L: List[int] = list()
x: int = 2
# STATE: L -> _@⊥; len(L) -> [0, 0]; x -> [2, 2]
if x in L:
    # STATE: L -> _@⊥; len(L) -> [0, 0]; x -> ⊥
    print(x)
else:
    raise ValueError
# FINAL: L -> _@⊥; len(L) -> [0, 0]; x -> ⊥
