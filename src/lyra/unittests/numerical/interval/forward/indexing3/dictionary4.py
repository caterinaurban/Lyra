
d0: Dict[int, int] = {0 : -1}
d1: Dict[int, Dict[int, int]] = dict()
# STATE: d0 -> 0@[-1, -1], _@⊥; d1 -> _@⊥; keys(d0) -> [0, 0]; keys(d1) -> ⊥; len(d0) -> [1, 1]; len(d1) -> [0, 0]; values(d0) -> [-1, -1]; values(d1) -> ⊥
d1[1] = d0
# FINAL: d0 -> 0@[-1, -1], _@⊥; d1 -> 1@[-1, 0], _@⊥; keys(d0) -> [0, 0]; keys(d1) -> [1, 1]; len(d0) -> [1, 1]; len(d1) -> [1, 1]; values(d0) -> [-1, -1]; values(d1) -> 0@[-1, -1], _@⊥

