
x: List[List[int]] = [[0], [0, 1], [0, 1, 2], [0, 1, 2, 3]]
# STATE: len(x) -> [4, 4]; x -> [0, 3]; y -> [-inf, inf]; z -> [-inf, inf]
y: int = x[3][3]
# STATE: len(x) -> [4, 4]; x -> [0, 3]; y -> [0, 3]; z -> [-inf, inf]
z: int = x[9][0]
# FINAL: len(x) -> ⊥; x -> ⊥; y -> ⊥; z -> ⊥
