# INITIAL [2:(Int, [-inf, inf]), (.ID=2 + 1) x [5:(Float, [-inf, inf])], 3 x [5:(Float, [-inf, inf])]]
N: int = int(input())
if N > 10:
    for i in range(N + 4):
        a: float = float(input())
else:
    for i in range(N + 1):
        a: float = float(input())
    for i in range(10):
        a: float = float(input())