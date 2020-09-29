
D: Dict[int, Dict[Tuple[int, int], List[int]]] = {0: {(1, 2): [3]}, 1: {(1, 2): [4]}}
r: Dict[Tuple[int, int], List[int]] = D[1]
# FINAL: D -> 0@[1, 3], 1@[1, 4], _@⊥; keys(D) -> [0, 1]; keys(r) -> _@[1, 2]; len(D) -> [2, 2]; len(r) -> [1, 1]; r -> (1, 2)@[3, 4], _@⊥; values(D) -> (1, 2)@[3, 4], _@⊥; values(r) -> [3, 4]
