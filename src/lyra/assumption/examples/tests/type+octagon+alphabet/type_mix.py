T: int = int(input())
for i in range(T):
    x: int = int(input())
    y: str = input()
    z: float = float(input())
    if x <= 10 and not y.isalpha():
        pass
    else:
        raise ValueError
    if x > z:
        pass
    else:
        raise ValueError
