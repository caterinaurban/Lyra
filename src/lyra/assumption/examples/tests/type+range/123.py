
# INITIAL:  3:(Integer, [-inf, inf]), 3.1 * 9:(Integer, [1, 3])
N: int = int(input())
one: int = 0
two: int = 0
three: int = 0
# STATE:  N * 9:(Integer, [1, 3])
for i in range(N):
    num: int = int(input())
    if num == 1:
        one: int = one + 1
    elif num == 2:
        two: int = two + 1
    elif num == 3:
        three: int = three + 1
    else:
        raise ValueError
# FINAL: ε
