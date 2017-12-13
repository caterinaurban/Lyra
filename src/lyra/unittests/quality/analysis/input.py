a: int = int(input())
# STATE a -> (Int, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf]), (Any, [-inf, inf]), (Float, [-inf, inf])]
if a > 10:
    # STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf]), (Any, [-inf, inf]), (Int, [-inf, inf])]
    b: int = int(input())
else:
    # STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf]), (Any, [-inf, inf]), (Float, [-inf, inf])]
    b: float = float(input())
# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf]), (Any, [-inf, inf])]
a: str = input()
# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf])]
c: float = float(input())
# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
a: int = int(input())
# FINAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), c -> (Any, [-inf, inf]), .IN -> []