
x: int = int(input())
# STATE: L -> _@[-inf, inf]; l -> _@[-inf, inf]; len(L) -> [0, inf]; len(l) -> [0, inf]; x -> [-inf, inf]; z -> [-inf, inf]
L: List[List[int]] = [[0], [1], [x]]
# STATE: L -> 2@[-inf, inf], _@[-inf, inf]; l -> _@[-inf, inf]; len(L) -> [3, inf]; len(l) -> [0, inf]; x -> [-inf, inf]; z -> [-inf, inf]
l: List[int] = L[2]
# STATE: L -> _@[-inf, inf]; l -> 0@[2, 2], _@[-inf, inf]; len(L) -> [0, inf]; len(l) -> [1, inf]; x -> [-inf, inf]; z -> [-inf, inf]
z: int = l[0]
# STATE: L -> _@[-inf, inf]; l -> _@[-inf, inf]; len(L) -> [0, inf]; len(l) -> [0, inf]; x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
