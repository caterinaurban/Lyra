# INITIAL [(Float, [-inf, 10]), (Int, [5, inf]), (Int, [2, 2])]
a: float = float(input())
if a > 10:
    raise ValueError
a: int = int(input())
if a < 5:
    raise ValueError
a: float = float(input())
if a != 2:
    raise ValueError
a: int = int(a)
