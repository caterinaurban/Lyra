# INITIAL [2:(Float, [-inf, inf]), 5:(Int, [-inf, 35])]
a: float = float(input())
x: int = 0
if a > 10:
    b: int = int(input())
    x: int = b - 13
else:
    c: int = int(input())
    x: int = c
if x > 22:
    raise ValueError

