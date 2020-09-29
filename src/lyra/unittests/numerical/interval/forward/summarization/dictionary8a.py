
x: int = int(input())
D: Dict[int, Dict[int, int]] = {3: {0: 0}, 4: {0: 1}, 5: {0: 2}}
d: Dict[int, int] = D[5]
z: int = d[0]
# FINAL: D -> [0, 5]; d -> [0, 2]; keys(D) -> [3, 5]; keys(d) -> [0, 2]; len(D) -> [3, 3]; len(d) -> [1, inf]; values(D) -> [0, 2]; values(d) -> [0, 2]; x -> [-inf, inf]; z -> [0, 2]
