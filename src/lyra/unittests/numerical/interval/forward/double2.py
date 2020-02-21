
def f(x: int):
    return x + 1

z: int = f(f(10))
# FINAL:  z -> [12, 12]