# INITIAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Int, [-inf, inf])]
a: int = int(input())
if a > 10:
    b: int = int(input())
    for i in range(4):
        a: int = a + 1
else:
    b: int = int(input())