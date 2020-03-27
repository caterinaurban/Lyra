
def f(x: int) -> int:
    return x + b

a: int = 3
b: int = 4
c: int = f(a)
# FINAL: a -> [3, 3]; b -> [4, 4]; c -> [7, 7]
