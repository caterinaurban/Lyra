
D: Dict[int, Dict[int, int]] = {0: {1: 3}, 1: {1: 4}}
r: Dict[int, int] = D[1]
# FINAL: D -> 0@[1, 3], 1@[1, 4], _@⊥; keys(D) -> [0, 1]; keys(r) -> [1, 1]; len(D) -> [2, 2]; len(r) -> [1, 1]; r -> 1@[3, 4], _@⊥; values(D) -> 1@[3, 4], _@⊥; values(r) -> [1, 4]
