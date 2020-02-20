
L: List[int] = [0, 1, 2]
x: int = 2
# STATE: L -> [0, 2]; len(L) -> [3, 3]; x -> [2, 2]
if x in L:
    # STATE: L -> [0, 2]; len(L) -> [3, 3]; x -> [2, 2]
    print(x)
else:
    raise ValueError
# FINAL: L -> [0, 2]; len(L) -> [3, 3]; x -> [2, 2]
