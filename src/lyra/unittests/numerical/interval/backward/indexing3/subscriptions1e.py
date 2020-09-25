
x: int = int(input())
# STATE: D -> _@[-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [0, inf]; values(D) -> _@[-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
D: Dict[int, List[int]] = {0: [0], 1: [1], 2: [x]}
# STATE: D -> 2@[-inf, inf], _@[-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [1, inf]; values(D) -> _@[-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
z: int = D[2][0]
# STATE: D -> _@[-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [0, inf]; values(D) -> _@[-inf, inf]; x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
