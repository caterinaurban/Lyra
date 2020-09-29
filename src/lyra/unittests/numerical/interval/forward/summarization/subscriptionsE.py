
D: Dict[int, Dict[int, int]] = {0: {1: 3}, 1: {1: 4}}
r: Dict[int, int] = D[1]
# FINAL: D -> [0, 4]; keys(D) -> [0, 1]; keys(r) -> [1, 4]; len(D) -> [2, 2]; len(r) -> [0, inf]; r -> [1, 4]; values(D) -> [1, 4]; values(r) -> [1, 4]
