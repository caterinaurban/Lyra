
def f(x: int) -> int:
    return x - 1

a: int = 2
c: int = f(f(a))
# RESULT: a -> [2, 2]; c -> [0, 0]
