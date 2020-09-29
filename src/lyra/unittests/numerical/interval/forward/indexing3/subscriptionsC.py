
s: str = 'abcd'
z: str = s[0]

L: List[Set[int]] = [{0}, {1, 2}, {3}]
x: Set[int] = L[1]

D: Dict[int, Dict[int, int]] = {0: {3: 4}, 1: {5 : 6}, 2: {7: 8, 9: 10}}
d: Dict[int, int] = D[2]
# FINAL: D -> 0@[3, 4], 1@[5, 6], 2@[7, 10], _@⊥; L -> 0@[0, 0], 1@[1, 2], 2@[3, 3], _@⊥; d -> _@[7, 10]; keys(D) -> [0, 2]; keys(d) -> [7, 10]; len(D) -> [3, 3]; len(L) -> [3, 3]; len(d) -> [0, inf]; len(s) -> [4, 4]; len(x) -> [0, inf]; len(z) -> [1, 1]; s -> 0@[-inf, inf], 1@[-inf, inf], 2@[-inf, inf], _@[-inf, inf]; values(D) -> _@[3, 10]; values(d) -> [7, 10]; x -> [1, 2]; z -> _@[-inf, inf]
