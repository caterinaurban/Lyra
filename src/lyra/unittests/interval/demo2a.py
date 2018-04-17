
# INITIAL: x -> [-inf, inf], a -> [-inf, inf]
x: int = int(input())
# STATE: x -> [-inf, inf], a -> [-inf, inf]
a: int = 0
# STATE: x -> [-inf, inf], a -> [0, 0]
if 3 > x:
    # STATE: x -> [-inf, 2], a -> [0, 0]
    a: int = x
    # STATE: x -> [-inf, 2], a -> [-inf, 2]
# STATE: x -> [-inf, inf], a -> [-inf, 2]
print(a)
# FINAL: x -> [-inf, inf], a -> [-inf, 2]
