
v1: int = 0
i: int = int(input())
d: Dict[int, int] = {3: 2}
# STATE: d -> 3@[2, 2], _@⊥; i -> [-inf, inf]; k -> [-inf, inf]; keys(d) -> [3, 3]; len(d) -> [1, 1]; v1 -> [0, 0]; v2 -> [-inf, inf]; values(d) -> [2, 2]
d[4]: int = 1
# STATE: d -> 3@[2, 2], 4@[1, 1], _@⊥; i -> [-inf, inf]; k -> [-inf, inf]; keys(d) -> [3, 4]; len(d) -> [2, 2]; v1 -> [0, 0]; v2 -> [-inf, inf]; values(d) -> [1, 2]
d[v1]: int = 7
# STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@⊥; i -> [-inf, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [3, 3]; v1 -> [0, 0]; v2 -> [-inf, inf]; values(d) -> [1, 7]
d[1]: int = v1
# STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 0]; i -> [-inf, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, 4]; v1 -> [0, 0]; v2 -> [-inf, inf]; values(d) -> [0, 7]
v2: int = d[3]
# STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 0]; i -> [-inf, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, 4]; v1 -> [0, 0]; v2 -> [2, 2]; values(d) -> [0, 7]
d[2]: int = 3 + v2
# STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [-inf, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, 5]; v1 -> [0, 0]; v2 -> [2, 2]; values(d) -> [0, 7]
if i >= 2:
    # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, 5]; v1 -> [0, 0]; v2 -> [2, 2]; values(d) -> [0, 7]
    i = i   # pass
    if i in d.keys():
        # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, 4]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, 5]; v1 -> [0, 0]; v2 -> [2, 2]; values(d) -> [0, 7]
        i = i  # pass
        v2: int = d[i]
        # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, 4]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, 5]; v1 -> [0, 0]; v2 -> [0, 5]; values(d) -> [0, 7]
    i = i  # pass
    # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, 5]; v1 -> [0, 0]; v2 -> [0, 5]; values(d) -> [0, 7]
    for k in d.keys():      # LOOP: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, inf]; v1 -> [0, 2]; v2 -> [0, 5]; values(d) -> [0, 7]
        # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, inf]; k -> [0, 4]; keys(d) -> [0, 4]; len(d) -> [4, inf]; v1 -> [0, 2]; v2 -> [0, 5]; values(d) -> [0, 7]
        i = i  # pass
        if k >= 3:
            # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, inf]; k -> [3, 4]; keys(d) -> [0, 4]; len(d) -> [4, inf]; v1 -> [0, 2]; v2 -> [0, 5]; values(d) -> [0, 7]
            i = i  # pass
            v1: int = d[k]
            # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, inf]; k -> [3, 4]; keys(d) -> [0, 4]; len(d) -> [4, inf]; v1 -> [1, 2]; v2 -> [0, 5]; values(d) -> [0, 7]
            d[k-2]: int = v1
            # STATE: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [2, inf]; k -> [3, 4]; keys(d) -> [0, 4]; len(d) -> [4, inf]; v1 -> [1, 2]; v2 -> [0, 5]; values(d) -> [0, 7]
# FINAL: d -> 0@[7, 7], 3@[2, 2], 4@[1, 1], _@[0, 5]; i -> [-inf, inf]; k -> [-inf, inf]; keys(d) -> [0, 4]; len(d) -> [4, inf]; v1 -> [0, 2]; v2 -> [0, 5]; values(d) -> [0, 7]
