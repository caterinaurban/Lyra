
D: Dict[int, int] = {1: 1, 2: 2, 3: 3, 4: 4}
x: int = int(input())
D[x] = 5
# FINAL: D -> 1@[1, 5], 2@[2, 5], 3@[3, 5], _@[4, 5]; keys(D) -> [-inf, inf]; len(D) -> [4, 5]; values(D) -> [1, 5]; x -> [-inf, inf]
