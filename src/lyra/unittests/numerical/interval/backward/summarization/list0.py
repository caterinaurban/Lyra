
L: List[int] = list()
for i in range(int(input())):
    L.append(int(input()))
# STATE: L -> [-inf, inf]; i -> [-inf, inf]; len(L) -> [3, inf]; x -> [-inf, inf]
x: int = L[2]
if x < 0:
    raise ValueError
