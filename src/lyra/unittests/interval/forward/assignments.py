
# INITIAL: x -> [-inf, inf], y -> [-inf, inf], a -> [-inf, inf]
x: int = 3
# STATE: x -> [3, 3], y -> [-inf, inf], a -> [-inf, inf]
y: int = 5
# STATE: x -> [3, 3], y -> [5, 5], a -> [-inf, inf]
a: int = x + y
# STATE: x -> [3, 3], y -> [5, 5], a -> [8, 8]
if a > 0:
    # STATE: x -> [3, 3], y -> [5, 5], a -> [8, 8]
    a: int = 2 * a
    # STATE: x -> [3, 3], y -> [5, 5], a -> [16, 16]
# STATE: x -> [3, 3], y -> [5, 5], a -> [16, 16]
print(a)
# FINAL: x -> [3, 3], y -> [5, 5], a -> [16, 16]
