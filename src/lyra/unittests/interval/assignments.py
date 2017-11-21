
# INITIAL: x -> [-inf, inf], y -> [-inf, inf], a -> [-inf, inf]
x: int = 3
# RESULT: x -> [3, 3], y -> [-inf, inf], a -> [-inf, inf]
y: int = 5
# RESULT: x -> [3, 3], y -> [5, 5], a -> [-inf, inf]
a: int = x + y
# RESULT: x -> [3, 3], y -> [5, 5], a -> [8, 8]
if a > 0:
    # RESULT: x -> [3, 3], y -> [5, 5], a -> [8, 8]
    a: int = 2 * a
    # RESULT: x -> [3, 3], y -> [5, 5], a -> [16, 16]
# RESULT: x -> [3, 3], y -> [5, 5], a -> [16, 16]
print(a)
# FINAL: x -> [3, 3], y -> [5, 5], a -> [16, 16]
