
# INITIAL: a -> [-inf, inf]; x -> [-inf, inf]
x: int = int(input())
# STATE: a -> [-inf, inf]; x -> [-inf, inf]
a: int = 0
# STATE: a -> [0, 0]; x -> [-inf, inf]
if 3 > x:
    # STATE: a -> [0, 0]; x -> [-inf, 2]
    a = x
    # STATE: a -> [-inf, 2]; x -> [-inf, 2]
# STATE: a -> [-inf, 2]; x -> [-inf, inf]
print(a)
# FINAL: a -> [-inf, 2]; x -> [-inf, inf]
