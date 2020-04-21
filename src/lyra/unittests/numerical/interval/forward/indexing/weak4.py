
D: Dict[int, int] = {1: 1, 2: 2, 3: 3, 4: 4}
x: int = int(input())
if x < 3:
    raise ValueError
D[x] = 5
# FINAL: D -> 1@[1, 1], 2@[2, 2], 3@[3, 5], _@[4, 5]; keys(D) -> [1, inf]; len(D) -> [4, 5]; values(D) -> [1, 5]; x -> [3, inf]
