
def f(x: int) -> int:
    return x - 1

a: int = 2
c: int = f(f(a))
# FINAL: a -> [2, 2]; c -> [0, 0]
