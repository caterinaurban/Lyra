# STATE a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, 9]), (Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Int, [-inf, 9]), b -> (Any, [-inf, inf]), .IN -> [(Int, [-inf, inf])]
b: int = int(input())
# STATE a -> (Int, [-inf, 9]), b -> (Any, [-inf, inf]), .IN -> []
b: int = a
# STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, 9]), .IN -> []
b: int = b + 1
# STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, 10]), .IN -> []
a: int = b

# STATE a -> (Int, [-inf, 10]), b -> (Any, [-inf, inf]), .IN -> []
if a > 10:
    # STATE a -> (⊥, ⊥), b -> (⊥, ⊥), .IN -> [] | []
    raise ValueError
