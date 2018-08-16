
# INITIAL: len([0, 0, 0]) * 5:(Integer, [0, inf])
l: List[int] = [0, 0, 0]
for i in range(len(l)):     # LOOP: len(l) * 5:(Integer, [0, inf])
    v: int = int(input())
    if v < 0:
        raise ValueError
    l[i]: int = v
# FINAL: ε
