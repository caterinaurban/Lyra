
# INITIAL: 3:(Integer, (∅, Σ)), 3.1 * [6:(Float, (∅, Σ)), 7:(String, ({'a', 'b', 'd'}, {'a', 'b', 'd'}))]
T:int = int(input())
# STATE: T * [6:(Float, (∅, Σ)), 7:(String, ({'a', 'b', 'd'}, {'a', 'b', 'd'}))]
for i in range(T):
    x: float = float(input())
    y: str = input()
    if x > 10 and y == 'abd':
        pass
    else:
        raise ValueError
# FINAL: ε
