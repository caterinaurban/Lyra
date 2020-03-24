
d0: Dict[int, int] = {0 : 1}
d1: Dict[int, int] = dict()
d1[d0[0]] = 2
# FINAL: d0 -> [0, 1]; d1 -> [1, 2]; keys(d0) -> [0, 0]; keys(d1) -> [1, 1]; len(d0) -> [1, 1]; len(d1) -> [1, 1]; values(d0) -> [1, 1]; values(d1) -> [2, 2]
