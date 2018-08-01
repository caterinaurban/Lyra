T: int = int(input())
for i in range(T):
    z: int = int(input())
    if z > 0:
        x: int = int(input())
        if x == 10:
            pass
        else:
            raise ValueError
    else:
        y: str = input()
        if y == 'abc':
            pass
        else:
            raise ValueError