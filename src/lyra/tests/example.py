def max(x: int, y: int):
  if x > y:
    return x
  else:
    return y


a: int = 10
b: int = 20

c: int = max(a, b)
d: int = max(c, 5)
print(d)