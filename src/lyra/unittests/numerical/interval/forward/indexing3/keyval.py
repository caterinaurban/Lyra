
D: Dict[str, Dict[int, int]] = {'a': {1: 0}, 'b': {1: 1}, 'c': {1: 2}, 'd': {1: 3}}
k: Set[str] = D.keys()
z: Set[Dict[int, int]] = D.values()
# FINAL: D -> "a"@[0, 1], "b"@[1, 1], "c"@[1, 2], _@[1, 3]; k -> [-inf, inf]; keys(D) -> 0@[-inf, inf], _@⊥; len(D) -> [4, 4]; len(k) -> [1, 1]; len(z) -> [1, 1]; values(D) -> 1@[0, 3], _@⊥; z -> [0, 3]
