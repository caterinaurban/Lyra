x: int = input()
if x > 10:
    y: int = int(input())
    if y + x <= 10:
        raise ValueError
    n: int = int(input())
    if n > 30:
        raise ValueError
else:
    z: float = float(input())
    m: int = int(input())
    if z + x <= 20:
        raise ValueError
    if m > 20:
        raise ValueError

# T: int = int(input())
# for i in range(T):
#     x: int = int(input())
#     y: str = input()
#     z: float = float(input())
#     if x <= 10 and not y.isalpha():
#         pass
#     else:
#         raise ValueError
#     if x > z:
#         pass
#     else:
#         raise ValueError

