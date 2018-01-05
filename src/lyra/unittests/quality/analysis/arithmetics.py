# STATE a -> (Any, [-inf, inf]), .IN -> [(Float, [-10, inf])]
a: float = float(input())

# STATE a -> (Float, [-10, inf]), .IN -> []
a: float = a + 1
# STATE a -> (Float, [-9, inf]), .IN -> []
a: float = a - 1
# STATE a -> (Float, [-10, inf]), .IN -> []
a: float = 1 + a
# STATE a -> (Float, [-9, inf]), .IN -> []
a: float = 1 - a

# STATE a -> (Float, [-inf, 10]), .IN -> []
if a > 10:
    # STATE a -> (⊥, ⊥), .IN -> [] | []
    raise Exception("NO")
