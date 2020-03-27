
def f(x: int) -> int:
    return x + 1

def g(x: int) -> int:
    return x - 1

z: int = g(f(10))
# FINAL: z -> [10, 10]