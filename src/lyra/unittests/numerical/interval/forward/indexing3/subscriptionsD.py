
L: List[Dict[int, int]] = [{0: 1}, {2: 3}, {4: 5}]
r: Dict[int, int] = L[1]
# FINAL: L -> 0@[0, 1], 1@[2, 3], 2@[4, 5], _@⊥; keys(r) -> [2, 3]; len(L) -> [3, 3]; len(r) -> [0, inf]; r -> _@[2, 3]; values(r) -> [2, 3]
