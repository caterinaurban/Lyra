# INITIAL [(Int, [-inf, 1]), (Int, [2, inf]), 10 x [(Float, [-inf, 3]), (Float, [4, inf]), 20 x [(Float, [-inf, 5]), (Float, [6, inf])], 30 x [(Float, [-inf, 7]), (Float, [8, inf])]]]
a: int = int(input())
if a > 1:
    raise ValueError
a: int = int(input())
if a < 2:
    raise ValueError
for i in range(10):
    b: float = float(input())
    if b > 3:
        raise ValueError
    b: float = float(input())
    if b < 4:
        raise ValueError
    for i in range(20):
        b: float = float(input())
        if b > 5:
            raise ValueError
        b: float = float(input())
        if b < 6:
            raise ValueError
    for i in range(30):
        b: float = float(input())
        if b > 7:
            raise ValueError
        b: float = float(input())
        if b < 8:
            raise ValueError
