# INITIAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> []
b: int = 0
# STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> []

while b < 10:
    # STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [] | [(Float, [-inf, inf])]
    c: int = float(input())
    # STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [] | []
    b: int = b + 1

# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
e: int = int(input())
# FINAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> []
