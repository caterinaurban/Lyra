# INITIAL [(Int, [-inf, inf]), 4 x [(Float, [-inf, inf])]]
a: int = int(input())
if a > 10:
    for i in range(4):
        b: int = float(input())
else:
    for i in range(4):
        if a > 10:
            b: int = int(input())
        else:
            b: int = float(input())