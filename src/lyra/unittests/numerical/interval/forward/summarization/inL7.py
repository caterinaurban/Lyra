
L: List[int] = list()
x: int = -9
# STATE: L -> ⊥; len(L) -> [0, 0]; x -> [-9, -9]
for x in L:
    # STATE: L -> ⊥; len(L) -> [0, 0]; x -> ⊥
    print(x)
# FINAL: L -> ⊥; len(L) -> [0, 0]; x -> [-9, -9]
