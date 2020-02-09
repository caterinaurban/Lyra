
def max(x: int, y: int):
  if x > y:
      return x
  else:
      return y

def min(x: int, y: int):
  if x < y:
      return x
  else:
      return y

a: int = 10
b: int = 20
c: int = max(a, b) if a > 0 and b > 0 else min(a, b)
# STATE: a -> [10, 10], b -> [20, 20], c -> [20, 20]

x: int = 0
for i in range(max(a, b)):
    x += 1
print(x)
