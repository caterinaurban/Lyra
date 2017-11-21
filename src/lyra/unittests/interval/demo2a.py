
# INITIAL: x -> [-inf, inf], a -> [-inf, inf]
x: int = int(input())
# RESULT: x -> [-inf, inf], a -> [-inf, inf]
a: int = 0
# RESULT: x -> [-inf, inf], a -> [0, 0]
if 3 > x:
    # RESULT: x -> [-inf, 2], a -> [0, 0]
    a: int = x
    # RESULT: x -> [-inf, 2], a -> [-inf, 2]
# RESULT: x -> [-inf, inf], a -> [-inf, 2]
print(a)
# FINAL: x -> [-inf, inf], a -> [-inf, 2]
