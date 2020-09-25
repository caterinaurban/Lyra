
x: int = int(input())
# STATE: x -> [2, 2]; z -> [-inf, inf]
z: int = {0: 0, 1: 1, 2: x}[2]
# STATE: x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
