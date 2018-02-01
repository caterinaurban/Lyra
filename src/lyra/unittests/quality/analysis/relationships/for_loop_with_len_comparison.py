# INITIAL [2:(Int, [-inf, inf]), (.ID=2 - 3) x [5:((Float, [-inf, inf]), [-.ID=5 + .VAR0 + 3 <= 0, .ID=5 - .ID=2 + 0 <= 0])]]
N: int = int(input())
l: List[int] = [1, 2, 3]
for i in range(N - 3):
    b: float = float(input())
    if b > N:
        raise ValueError
    if b < len(l):
        raise ValueError