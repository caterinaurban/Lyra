
# INITIAL: a -> [-inf, inf], b -> [-inf, inf]
a: int = int(input())
# STATE: a -> [-inf, inf], b -> [-inf, inf]
b: int = 1 if 1 <= a <= 9 else 2
# FINAL: a -> [-inf, inf], b -> [1, 2]
