
x: int = int(input())
# STATE: x -> [2, 2]; z -> [-inf, inf]
z: int = [0, 1, 2][x]
# STATE: x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError