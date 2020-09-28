
D: Dict[str, Dict[int, int]] = {'a': {1: 0}, 'b': {1: 1}, 'c': {1: 2}, 'd': {1: 3}}
k: Set[str] = D.keys()
z: Set[Dict[int, int]] = D.values()
# FINAL: D -> [-inf, inf]; k -> [-inf, inf]; keys(D) -> [-inf, inf]; len(D) -> [4, 4]; len(k) -> [0, inf]; len(z) -> [0, inf]; values(D) -> [0, 3]; z -> [0, 3]
