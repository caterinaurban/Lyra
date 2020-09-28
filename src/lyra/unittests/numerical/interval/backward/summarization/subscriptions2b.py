
x: int = int(input())
# STATE: x -> [-inf, inf]; z -> [-inf, inf]
z: int = {0: 0, 1: 1, 2: 2}[x]
# STATE: x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError