# INITIAL [(Float, [-10, inf])]
a: float = float(input())

# STATE a -> (Float), .IN -> [], .REL -> a -> [-10, inf]
a: float = a + 1
# STATE a -> (Float), .IN -> [], .REL -> a -> [-9, inf]
a: float = a - 1
# STATE a -> (Float), .IN -> [], .REL -> a -> [-10, inf]
a: float = 1 + a
# STATE a -> (Float), .IN -> [], .REL -> a -> [-9, inf]
a: float = 1 - a

# STATE a -> (Float), .IN -> [], .REL -> a -> [-inf, 10]
if a > 10:
    raise Exception("NO")
