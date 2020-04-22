
d1: Dict[int, Dict[int, int]] = dict()
# STATE: d1 -> _@⊥; keys(d1) -> ⊥; len(d1) -> [0, 0]; values(d1) -> ⊥
d1[1] = {0: -1}
# STATE: d1 -> 1@[-1, 0], _@⊥; keys(d1) -> [1, 1]; len(d1) -> [1, 1]; values(d1) -> 0@[-1, -1], _@⊥
d1[1][0] = -9
# STATE: d1 -> 1@[-9, 0], _@⊥; keys(d1) -> [1, 1]; len(d1) -> [1, 1]; values(d1) -> 0@[-9, -1], _@⊥
d1[1][23] = -9
# FINAL: d1 -> 1@[-9, 23], _@⊥; keys(d1) -> [1, 1]; len(d1) -> [1, 1]; values(d1) -> 0@[-9, -1], _@[-9, -9]
