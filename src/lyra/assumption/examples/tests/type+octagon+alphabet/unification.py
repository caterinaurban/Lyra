x: int = input()
if x > 10:
    y: int = int(input())
    if y + x <= 10:
        raise ValueError
    n: int = int(input())
    if n > 30:
        raise ValueError
else:
    z: float = float(input())
    m: int = int(input())
    if z + x <= 20:
        raise ValueError
    if m > 20:
        raise ValueError
# Assumptions: 1:(Integer, ⊤, ⊤, (∅, Σ)), 3:(Float, ⊤, OCT(3.1 + 1.1 - 11.0 >= 0), (∅, Σ)),
# 6:(Integer, ⊤, OCT(30.0 >= 6.1), (∅, Σ))
