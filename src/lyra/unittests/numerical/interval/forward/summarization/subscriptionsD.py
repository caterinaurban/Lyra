
L: List[Dict[int, int]] = [{0: 1}, {2: 3}, {4: 5}]
r: Dict[int, int] = L[1]
# FINAL: L -> [0, 5]; keys(r) -> [0, 5]; len(L) -> [3, 3]; len(r) -> [0, inf]; r -> [0, 5]; values(r) -> [0, 5]
