
x: int = int(input())
D: Dict[int, Dict[int, int]] = {3: {0: 0}, 4: {0: 1}, 5: {0: 2}}
d: Dict[int, int] = D[5]
z: int = d[0]
# FINAL: D -> 3@[0, 0], 4@[0, 1], 5@[0, 2], _@⊥; d -> 0@[0, 2], _@⊥; keys(D) -> [3, 5]; keys(d) -> [0, 0]; len(D) -> [3, 3]; len(d) -> [1, 1]; values(D) -> 0@[0, 2], _@⊥; values(d) -> [0, 2]; x -> [-inf, inf]; z -> [0, 2]
