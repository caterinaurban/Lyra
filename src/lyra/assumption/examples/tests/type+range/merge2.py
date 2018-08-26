# INITIAL: 3:(Integer, [-inf, inf]), 5:(Integer, [-inf, 5]), 6:(Integer, [3, inf])
z: int = int(input())
if z <= 3:
    x: int = int(input())
    y: int = int(input())
    if x <= 3 <= y:
        pass
    else:
        raise ValueError
else:
    y: int = int(input())
    x: int = int(input())
    if y <= 5 <= x:
        pass
    else:
        raise ValueError

# 2:(Integer, ⊤, ⊤, (∅, Σ)), 4:(Integer, ⊤, OCT(5.0 >= 4.1), (∅, Σ)), 5:(Integer, >0, OCT(5.1 - 3.0 >= 0,5.1 >= 4.1,5.0 >= 4.1), (∅, Σ))