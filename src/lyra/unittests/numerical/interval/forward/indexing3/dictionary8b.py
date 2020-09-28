
x: int = int(input())
d: Dict[int, int] = {3: {0: 0}, 4: {0: 1}, 5: {0: 2}}[5]
z: int = d[0]
# FINAL: d -> 0@[0, 2], _@⊥; keys(d) -> [0, 0]; len(d) -> [1, inf]; values(d) -> [0, 2]; x -> [-inf, inf]; z -> [0, 2]
