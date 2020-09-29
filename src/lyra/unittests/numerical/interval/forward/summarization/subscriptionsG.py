
D: Dict[int, Dict[Tuple[int, int], List[int]]] = {0: {(1, 2): [3]}, 1: {(1, 2): [4]}}
r: Dict[Tuple[int, int], List[int]] = D[1]
# FINAL: D -> [0, 4]; keys(D) -> [0, 1]; keys(r) -> [1, 4]; len(D) -> [2, 2]; len(r) -> [0, inf]; r -> [1, 4]; values(D) -> [1, 4]; values(r) -> [1, 4]
