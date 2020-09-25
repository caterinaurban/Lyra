
x: int = int(input())
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [0, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
D: Dict[int, List[int]] = {0: [0], 1: [1], 2: [x]}
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [1, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
z: int = D[2][0]
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [0, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
