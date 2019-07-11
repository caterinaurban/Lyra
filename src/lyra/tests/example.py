def max(x: int, y: int):
  while(x > y):
     x-= 1
  z: int = 2 + x
  print(z)
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

while a > 10:
  a = a - 1

if a != 10 or b != 20 or c != 20 or d != 50:
  raise Exception
