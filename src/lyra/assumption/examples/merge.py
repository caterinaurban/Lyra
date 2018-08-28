
# INITIAL: 3:(Integer, [-inf, inf]), 5:(Integer, [-inf, 5]), 6:(Integer, [3, inf])
# z: int = int(input())
# if z <= 3:
#     x: int = int(input())
#     y: int = int(input())
#     if x <= 3 <= y:
#         pass
#     else:
#         raise ValueError
# else:
#     y: int = int(input())
#     x: int = int(input())
#     if y <= 5 <= x:
#         pass
#     else:
#         raise ValueError
x: int = int(input())
y: int = int(input())
if x > y:
    raise ValueError
