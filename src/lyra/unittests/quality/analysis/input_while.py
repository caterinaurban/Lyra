# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> T
b: int = 0
# STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> T
while b < 10:
    # STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [] | [(Int, [-inf, inf])]
    c: int = int(input())
    # STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [] | []
    b: int = b + 1

# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
e: int = int(input())
# FINAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), e -> (Any, [-inf, inf]), .IN -> []
