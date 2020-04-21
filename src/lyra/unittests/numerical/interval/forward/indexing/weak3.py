
D: Dict[int, int] = {1: 1, 2: 2, 3: 3, 4: 4}
x: int = int(input())
if x < 3:
    raise ValueError
y: int = D[x]
# FINAL: D -> 1@[1, 1], 2@[2, 2], 3@[3, 3], _@[4, 4]; keys(D) -> [1, 4]; len(D) -> [4, 4]; values(D) -> [1, 4]; x -> [3, inf]; y -> [3, 4]
