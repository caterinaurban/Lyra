# STATE a -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), 10 x [(Float, [-inf, inf])]]
a: int = int(input())
i: int = 0
for i in range(10):
    a: int = a + 1
for i in range(10):
    if a > 10:
        b: int = float(input())
    else:
        b: int = int(input())
for i in range(10):
    a: int = a + 1
