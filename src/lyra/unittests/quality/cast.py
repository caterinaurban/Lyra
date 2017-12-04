
a: int = 10

b: float = 1.1
# STATE: a -> (Int, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> []
b: float = int(a)
# FINAL: a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> []
