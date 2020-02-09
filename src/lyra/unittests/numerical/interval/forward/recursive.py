def sum(n: int) -> int:
  if n == 0:
      return 0
  else:
      return n + sum(n-1)

x: int = 5
result: int = sum(5)