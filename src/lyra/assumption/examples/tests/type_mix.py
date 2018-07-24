T: int = int(input())
for i in range(T):
    x: int = int(input())
    y: str = input()

    if x + 10 <= 0 and y == "abc":
        pass
    else:
        raise ValueError