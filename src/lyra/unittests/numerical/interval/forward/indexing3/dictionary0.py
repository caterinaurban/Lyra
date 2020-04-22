
D: Dict[int, int] = {1: 1, 2: 2}
y: int = D[2]
# FINAL: D -> 1@[1, 1], 2@[2, 2], _@⊥; keys(D) -> [1, 2]; len(D) -> [2, 2]; values(D) -> [1, 2]; y -> [2, 2]
