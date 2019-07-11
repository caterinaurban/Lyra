def max(x: int, y: int):
  if x > y:
    return x
  else:
    return y


a: int = 10
b: int = 20

c: int = max(a, b)

e: int = 50
d: int = max(c, e)
print(d)

if a != 10 or b != 20 or c != 20 or d != 50:
  raise Exception
