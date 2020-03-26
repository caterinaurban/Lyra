
def max(x: int, y: int):
  if x > y:
      return x
  else:
      return y

a: int = 10
b: int = 20
c: int = max(a, b)
x: int = 0
for i in range(c):
    x += 1
    # STATE: a -> [10, 10]; b -> [20, 20]; c -> [20, 20]; i -> [0, 19]; x -> [1, inf]
