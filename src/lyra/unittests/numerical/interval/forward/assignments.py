
# INITIAL: a -> [-inf, inf], x -> [-inf, inf], y -> [-inf, inf]
x: int = 3
# STATE: a -> [-inf, inf], x -> [3, 3], y -> [-inf, inf]
y: int = 5
# STATE: a -> [-inf, inf], x -> [3, 3], y -> [5, 5]
a: int = x + y
# STATE: a -> [8, 8], x -> [3, 3], y -> [5, 5]
if a > 0:
    # STATE: a -> [8, 8], x -> [3, 3], y -> [5, 5]
    a: int = 2 * a
    # STATE: a -> [16, 16], x -> [3, 3], y -> [5, 5]
# STATE: a -> [16, 16], x -> [3, 3], y -> [5, 5]
print(a)
# FINAL: a -> [16, 16], x -> [3, 3], y -> [5, 5]
