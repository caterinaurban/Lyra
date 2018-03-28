x: int = int(input())
if x < 10:
    raise ValueError
for i in range(x):
    y: float = float(input())
    if y < x:
        raise ValueError
data: List[str] = input().split(",")
if x > 30:
    print(data[3])
else:
    print(data[8])
