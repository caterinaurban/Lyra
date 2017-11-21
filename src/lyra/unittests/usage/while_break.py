n: int = int(input())
x: int = int(input())
i: int = 0
while i < n:
    x: int = x / 2
    if x < 1:
        if i > 3:
            x: int = 0
            break
        continue
    else:
        x: int = 1
    print(x)
    i: int = i + 1
else:
    x: int = 3

while i < n:
    break
print(n)
