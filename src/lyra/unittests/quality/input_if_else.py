# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf]), (Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Int, [10, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf])]
if a > 10:
    # STATE a -> (Int, [11, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Int, [-inf, inf])]
    b: int = int(input())
else:
    # STATE a -> (Int, [-inf, 10]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf])]
    b: float = float(input())
# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
a: int = int(input())