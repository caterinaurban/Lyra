
# INITIAL a -> (Any, [-inf, inf]), .IN -> [(Any, [-inf, inf]), (Int, [-inf, inf]), (Int, [-inf, inf])]
a: str = input()
# STATE a -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf]), (Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
a: str = input()
a: int = int(a)
# FINAL a -> (Any, [-inf, inf]), .IN -> []