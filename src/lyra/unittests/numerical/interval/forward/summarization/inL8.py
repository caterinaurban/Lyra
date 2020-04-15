
L: List[int] = [0, 1, 2]
x: int = -9
# STATE: L -> [0, 2]; len(L) -> [3, 3]; x -> [-9, -9]
for x in L:
    print(x)
# FINAL: L -> [0, 2]; len(L) -> [3, 3]; x -> [-9, 2]
