# INITIAL a -> (Any, [-inf, inf]), b -> (Any, [-inf, inf]), .IN -> [(Float, [5, 40]), (Float, [10, 20])]
a: float = float(input())
b: float = float(input())

# STATE a -> (Float, [5, 40]), b -> (Float, [10, 20]), .IN -> []
if b < 10:
    # STATE a -> (⊥, ⊥), b -> (⊥, ⊥), .IN -> [] | []
    raise ValueError

# STATE a -> (Float, [5, 40]), b -> (Float, [-inf, 20]), .IN -> [] | []
if b > 20:
    # STATE a -> (⊥, ⊥), b -> (⊥, ⊥), .IN -> [] | []
    raise ValueError("Error!")

# STATE a -> (Float, [5, 40]), b -> (Any, [-inf, inf]), .IN -> [] | []

if a < 5:
    # STATE a -> (⊥, ⊥), b -> (⊥, ⊥), .IN -> [] | []
    raise Exception

# STATE a -> (Float, [-inf, 40]), b -> (Any, [-inf, inf]), .IN -> [] | []
if a > 40:
    # STATE a -> (⊥, ⊥), b -> (⊥, ⊥), .IN -> [] | []
    raise Exception("Error!")
