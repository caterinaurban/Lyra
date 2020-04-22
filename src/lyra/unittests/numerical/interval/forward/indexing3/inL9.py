
L: List[int] = list()
for i in range(int(input())):
    L.append(int(input()))
x: int = -9
# STATE: L -> _@[-inf, inf]; i -> [-inf, inf]; len(L) -> [0, inf]; x -> [-9, -9]
for x in L:
    print(x)
# FINAL: L -> _@[-inf, inf]; i -> [-inf, inf]; len(L) -> [0, inf]; x -> [-inf, inf]
