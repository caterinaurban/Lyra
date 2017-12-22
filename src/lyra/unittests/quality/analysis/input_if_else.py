# INITIAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Float, [-inf, inf]), (Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Int, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Float, [-inf, inf]), (Int, [-inf, inf])]
if a > 10:
    # STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])] | [(Int, [-inf, inf])]
    b: int = int(input())
else:
    # STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])] | [(Float, [-inf, inf])]
    b: float = float(input())
# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])] | []

a: int = int(input())
# FINAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> []
