a: int = int(input())
# STATE a -> (Any, [-inf, inf]), i -> (Int, [-inf, inf]), e -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [3 x [(Float, [-inf, inf]), 4 x [(Int, [-inf, inf])], 2 x [(Float, [-inf, inf])]], (Int, [-inf, inf])]
for i in range(1, 10, 4):
    c: int = float(input())
    for i in range(1, 5):
        c: int = int(input())
    for i in range(2):
        c: int = float(input())

# STATE a -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
e: int = int(input())
# FINAL a -> (Any, [-inf, inf]), i -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> []
