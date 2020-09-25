
x: int = int(input())
# STATE: L -> [-inf, inf]; l -> [-inf, inf]; len(L) -> [0, inf]; len(l) -> [0, inf]; x -> [-inf, inf]; z -> [-inf, inf]
L: List[List[int]] = [[0], [1], [x]]
# STATE: L -> [-inf, inf]; l -> [-inf, inf]; len(L) -> [3, inf]; len(l) -> [0, inf]; x -> [-inf, inf]; z -> [-inf, inf]
l: List[int] = L[2]
# STATE: L -> [-inf, inf]; l -> [-inf, inf]; len(L) -> [0, inf]; len(l) -> [1, inf]; x -> [-inf, inf]; z -> [-inf, inf]
z: int = l[0]
# STATE: L -> [-inf, inf]; l -> [-inf, inf]; len(L) -> [0, inf]; len(l) -> [0, inf]; x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
