
D: Dict[int, List[int]] = {1: [2], 2: [3, 4]}
L: List[List[int]] = [[], [2], [3, 4]]
# STATE: D -> [1, 4]; L -> [2, 4]; keys(D) -> [1, 2]; len(D) -> [2, 2]; len(L) -> [3, 3]; values(D) -> [2, 4]; y -> [-inf, inf]; z -> [-inf, inf]
y: int = D[2][1]
z: int = L[2][1]
# STATE: D -> [1, 4]; L -> [2, 4]; keys(D) -> [1, 2]; len(D) -> [2, 2]; len(L) -> [3, 3]; values(D) -> [2, 4]; y -> [2, 4]; z -> [2, 4]
