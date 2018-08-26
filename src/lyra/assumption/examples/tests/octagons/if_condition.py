# 2:(Integer, ⊤, ⊤, (∅, Σ)), 3:(Integer, ⊤, OCT(199.0 >= 3.1 + 2.1), (∅, Σ))
x: int = int(input())
y: int = int(input())
a: int = x + 1
if y + a > 200:
    raise ValueError