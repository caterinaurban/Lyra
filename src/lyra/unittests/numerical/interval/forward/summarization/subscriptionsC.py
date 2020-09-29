
s: str = 'abcd'
z: str = s[0]

L: List[Set[int]] = [{0}, {1, 2}, {3}]
x: Set[int] = L[1]

D: Dict[int, Dict[int, int]] = {0: {3: 4}, 1: {5 : 6}, 2: {7: 8, 9: 10}}
d: Dict[int, int] = D[2]
# FINAL: D -> [0, 10]; L -> [0, 3]; d -> [3, 10]; keys(D) -> [0, 2]; keys(d) -> [3, 10]; len(D) -> [3, 3]; len(L) -> [3, 3]; len(d) -> [0, inf]; len(s) -> [4, 4]; len(x) -> [0, inf]; len(z) -> [1, 1]; s -> [-inf, inf]; values(D) -> [3, 10]; values(d) -> [3, 10]; x -> [0, 3]; z -> [-inf, inf]
