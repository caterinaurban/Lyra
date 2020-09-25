
x: int = int(input())
# STATE: x -> [-inf, inf]; z -> [-inf, inf]
z: int = [[0], [1], [x]][2][0]
# STATE: x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
