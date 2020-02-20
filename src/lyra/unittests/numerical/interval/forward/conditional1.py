
# INITIAL: a -> [-inf, inf]; b -> [-inf, inf]
a: int = int(input())
# STATE: a -> [-inf, inf]; b -> [-inf, inf]
if 1 <= a <= 9:
    # STATE: a -> [1, 9]; b -> [-inf, inf]
    b: int = 1
    # STATE: a -> [1, 9]; b -> [1, 1]
else:
    # STATE: a -> [-inf, inf]; b -> [-inf, inf]
    b: int = 2
    # STATE: a -> [-inf, inf]; b -> [2, 2]
# FINAL: a -> [-inf, inf]; b -> [1, 2]
