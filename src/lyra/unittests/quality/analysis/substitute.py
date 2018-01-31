# INITIAL [2:(Int, [-inf, 9]), 4:(Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Int, [-inf, 9]), b -> (Any, [-inf, inf]), .IN -> [4:(Int, [-inf, inf])], .REL -> []
b: int = int(input())
# STATE a -> (Int, [-inf, 9]), b -> (Any, [-inf, inf]), .IN -> [], .REL -> []
b: int = a
# STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, 9]), .IN -> [], .REL -> []
b: int = b + 1
# STATE a -> (Any, [-inf, inf]), b -> (Int, [-inf, 10]), .IN -> [], .REL -> []
a: int = b

# STATE a -> (Int, [-inf, 10]), b -> (Any, [-inf, inf]), .IN -> [], .REL -> []
if a > 10:
    raise ValueError
