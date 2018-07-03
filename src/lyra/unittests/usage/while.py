n: int = int(input())
x: int = int(input())
i: int = 0
# STATE: i -> N, n -> N, x -> W
while i < n:
    x: int = i / 2  # BUG: should be x = x / 2
    i: int = i + 1
else:
    x: int = -1
print(x)
