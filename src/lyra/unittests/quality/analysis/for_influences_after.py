# INITIAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), i -> (Int, [-inf, inf]), .IN -> [(Int, [-inf, 10]), (Int, [-inf, inf])]
a: int = int(input())
b: int = int(input())
for i in range(100):
    a: int = a + 1
for i in range(100):
    b: int = b - 1
if a > 10:
    raise ValueError
if b > 20:
    raise ValueError
