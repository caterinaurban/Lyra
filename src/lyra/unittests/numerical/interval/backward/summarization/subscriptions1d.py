
x: int = int(input())
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; l -> [-inf, inf]; len(D) -> [0, inf]; len(l) -> [0, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
D: Dict[int, List[int]] = {0: [0], 1: [1], 2: [x]}
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; l -> [-inf, inf]; len(D) -> [1, inf]; len(l) -> [0, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
l: List[int] = D[2]
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; l -> [-inf, inf]; len(D) -> [0, inf]; len(l) -> [1, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
z: int = l[0]
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; l -> [-inf, inf]; len(D) -> [0, inf]; len(l) -> [0, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
