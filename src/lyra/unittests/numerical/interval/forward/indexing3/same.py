
b: bool = bool(input())
D1: Dict[int, int] = dict()
D2: Dict[int, int] = dict()
if b:
    x: int = 3
    D1[x] = 0
    # STATE: D1 -> 3@[0, 0], _@⊥; D2 -> _@⊥; b -> [1, 1]; keys(D1) -> [3, 3]; keys(D2) -> ⊥; len(D1) -> [1, 1]; len(D2) -> [0, 0]; values(D1) -> [0, 0]; values(D2) -> ⊥; x -> [3, 3]
    D1[3] = 1
    # STATE: D1 -> 3@[1, 1], _@⊥; D2 -> _@⊥; b -> [1, 1]; keys(D1) -> [3, 3]; keys(D2) -> ⊥; len(D1) -> [1, 1]; len(D2) -> [0, 0]; values(D1) -> [1, 1]; values(D2) -> ⊥; x -> [3, 3]
else:
    x: int = 4
    D1[x] = 0
    # STATE: D1 -> 4@[0, 0], _@⊥; D2 -> _@⊥; b -> [0, 0]; keys(D1) -> [4, 4]; keys(D2) -> ⊥; len(D1) -> [1, 1]; len(D2) -> [0, 0]; values(D1) -> [0, 0]; values(D2) -> ⊥; x -> [4, 4]
    D1[3] = 1
    # STATE: D1 -> 3@[1, 1], 4@[0, 0], _@⊥; D2 -> _@⊥; b -> [0, 0]; keys(D1) -> [3, 4]; keys(D2) -> ⊥; len(D1) -> [2, 2]; len(D2) -> [0, 0]; values(D1) -> [0, 1]; values(D2) -> ⊥; x -> [4, 4]
D2[x] = 0
D2[3] = 1
# FINAL: D1 -> 3@[1, 1], _@[0, 0]; D2 -> 3@[1, 1], _@[0, 0]; b -> [0, 1]; keys(D1) -> [3, 4]; keys(D2) -> [3, 4]; len(D1) -> [1, 2]; len(D2) -> [1, 2]; values(D1) -> [0, 1]; values(D2) -> [0, 1]; x -> [3, 4]
