# INITIAL [2:(Float, [-10, inf])]
a: float = float(input())

# STATE a -> (Float, [-10, inf]), .IN -> [], .REL -> {}
a: float = a + 1
# STATE a -> (Float, [-9, inf]), .IN -> [], .REL -> {}
a: float = a - 1
# STATE a -> (Float, [-10, inf]), .IN -> [], .REL -> {}
a: float = 1 + a
# STATE a -> (Float, [-9, inf]), .IN -> [], .REL -> {}
a: float = 1 - a

# STATE a -> (Float, [-inf, 10]), .IN -> [], .REL -> {}
if a > 10:
    raise Exception("NO")
