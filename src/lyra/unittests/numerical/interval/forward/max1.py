
def max(x: int, y: int) -> int:
  if x > y:
      return x
  else:
      return y

def min(x: int, y: int) -> int:
  if x < y:
      return x
  else:
      return y

a: int = 10
b: int = 20
c: int = max(a, b) if a > 0 and b > 0 else min(a, b)
# FINAL: a -> [10, 10]; b -> [20, 20]; c -> [20, 20]
