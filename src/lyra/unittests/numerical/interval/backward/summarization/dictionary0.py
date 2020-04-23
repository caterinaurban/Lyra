
D: Dict[int, int] = {0: 0, 1: 1, 2: 2}
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [1, inf]; values(D) -> [-inf, inf]; x -> [-inf, inf]
x: int = D[2]
# STATE: D -> [-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [0, inf]; values(D) -> [-inf, inf]; x -> [0, inf]
if x < 0:
    raise ValueError
