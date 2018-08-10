
# INITIAL:  3:(Integer, [-inf, inf]), 3.1 * 8:(Integer, [-inf, inf])
N: int = int(input())
neg: int = 0
pos: int = 0
# STATE: N * 8:(Integer, [-inf, inf])
for i in range(N):
    num: int = int(input())
    if num < 0:
        neg: int = neg + 1
    elif num > 0:
        post: int = pos + 1
# FINAL: ε
