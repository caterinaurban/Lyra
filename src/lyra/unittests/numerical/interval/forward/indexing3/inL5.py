
L: List[int] = list()
for i in range(int(input())):
    L.append(int(input()))
x: int = -9
# STATE: L -> _@[-inf, inf]; i -> [-inf, inf]; len(L) -> [0, inf]; x -> [-9, -9]
if x in L:
    # STATE: L -> _@[-inf, inf]; i -> [-inf, inf]; len(L) -> [0, inf]; x -> [-9, -9]
    print(x)
else:
    raise ValueError
# FINAL: L -> _@[-inf, inf]; i -> [-inf, inf]; len(L) -> [0, inf]; x -> [-9, -9]
