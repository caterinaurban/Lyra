
x: int = int(input())
# STATE: D -> _@[-inf, inf]; keys(D) -> [-inf, inf]; l -> _@[-inf, inf]; len(D) -> [0, inf]; len(l) -> [0, inf]; values(D) -> _@[-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
D: Dict[int, List[int]] = {0: [0], 1: [1], 2: [x]}
# STATE: D -> 2@[-inf, inf], _@[-inf, inf]; keys(D) -> [-inf, inf]; l -> _@[-inf, inf]; len(D) -> [1, inf]; len(l) -> [0, inf]; values(D) -> _@[-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
l: List[int] = D[2]
# STATE: D -> _@[-inf, inf]; keys(D) -> [-inf, inf]; l -> 0@[2, 2], _@[-inf, inf]; len(D) -> [0, inf]; len(l) -> [1, inf]; values(D) -> _@[-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
z: int = l[0]
# STATE: D -> _@[-inf, inf]; keys(D) -> [-inf, inf]; l -> _@[-inf, inf]; len(D) -> [0, inf]; len(l) -> [0, inf]; values(D) -> _@[-inf, inf]; x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
