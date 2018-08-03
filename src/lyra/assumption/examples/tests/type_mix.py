x: int = input()
if x > 10:
    y: int = int(input())
    if y > 10:
        pass
    else:
        raise ValueError
else:
    z: int = int(input())
    if z > 10:
        pass
    else:
        raise ValueError
# T: int = int(input())
# for i in range(T):
#     x: int = int(input())
#     y: str = input()
#     z: float = float(input())
#     if x <= 10 and y == 'abc':
#         pass
#     else:
#         raise ValueError
#     if x > z:
#         pass
#     else:
#         raise ValueError
