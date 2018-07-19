
x: int = int(input()) + int(input())
for i in range(x):
    y: float = float(input())
    if y <= 3.0:
        print(y)
    else:
        raise ValueError
z: str = input()
