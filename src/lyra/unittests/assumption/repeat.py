
# INITIAL: 3:(Integer, [-inf, inf]), 3:(Integer, [-inf, inf]), 3.1 + 3.2 * 5:(Float, [-inf, 3.0]), 10:(String, [-inf, inf])
x: int = int(input()) + int(input())
for i in range(x):
    y: float = float(input())
    if y <= 3.0:
        print(y)
    else:
        raise ValueError
z: str = input()
