# STATE a -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (10 x [(Float, [-inf, inf])]), (Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(10 x [(Float, [-inf, inf])]), (Int, [-inf, inf])]
i: int = 0
# STATE a -> (Any, [-inf, inf]), i -> (Int, [-inf, 0]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(10 x [(Float, [-inf, inf])]), (Int, [-inf, inf])]
for i in range(10):
    c: int = float(input())

# STATE a -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
e: int = int(input())
# FINAL a -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> []
