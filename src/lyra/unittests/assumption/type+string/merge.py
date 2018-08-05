
# INITIAL: 3:(Integer, (∅, Σ)), 3.1 * [6:(Integer, (∅, Σ)), 8:(String, (∅, Σ))]
T: int = int(input())
# STATE: T * [6:(Integer, (∅, Σ)), 8:(String, (∅, Σ))]
for i in range(T):
    z: int = int(input())
    if z > 0:
        x: int = int(input())
        if x == 10:
            pass
        else:
            raise ValueError
    else:
        y: str = input()
        if y == 'abc':
            pass
        else:
            raise ValueError
# FINAL: ε
