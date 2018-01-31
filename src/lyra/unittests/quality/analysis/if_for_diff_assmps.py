# INITIAL [2:(Int, [-inf, inf]), 3 x [5:(Float, [-inf, 40])], 5:(Float, [-inf, 10])]
a: int = int(input())
if a > 10:
    for i in range(20):
        c: float = float(input())
        if c > 10:
            raise ValueError
else:
    for i in range(3):
        c: int = int(input())
        if c > 40:
            raise ValueError
c: float = float(input())
if c > 4:
    raise ValueError

