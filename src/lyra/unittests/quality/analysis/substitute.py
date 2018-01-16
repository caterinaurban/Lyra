# INITIAL [(Int, [-inf, 9]), (Int, [-inf, inf])]
a: int = int(input())
# STATE a -> (Int), b -> (Any), .IN -> [(b, (Int), a -> [-inf, 9], b -> [-inf, inf], {'b': [1]})], .REL -> a -> [-inf, 9], b -> [-inf, inf]
b: int = int(input())
# STATE a -> (Int), b -> (Any), .IN -> [], .REL -> a -> [-inf, 9], b -> [-inf, inf]
b: int = a
# STATE a -> (Any), b -> (Int), .IN -> [], .REL -> a -> [-inf, inf], b -> [-inf, 9]
b: int = b + 1
# STATE a -> (Any), b -> (Int), .IN -> [], .REL -> a -> [-inf, inf], b -> [-inf, 10]
a: int = b

# STATE a -> (Int), b -> (Any), .IN -> [], .REL -> a -> [-inf, 10], b -> [-inf, inf]
if a > 10:
    raise ValueError
