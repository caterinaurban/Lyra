
def f(x: int):
    return x - 1

a: int = int(input())
# STATE: a -> [2, inf], c -> [-inf, inf]
c: int = f(f(a))
# STATE: a -> [-inf, inf], c -> [0, inf]

if c < 0:
    raise ValueError
