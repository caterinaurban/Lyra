
# INITIAL: 2 * [6:(Float, [-inf, inf]), ★]
b: float = 0
for i in range(2):
    if b > 0:
        a: int = int(input())
        if a < b:
            raise ValueError
    b: float = float(input())
# FINAL: ε
