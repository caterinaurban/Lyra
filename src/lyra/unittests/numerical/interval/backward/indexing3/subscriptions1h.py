
x: int = int(input())
# STATE: x -> [2, 2]; z -> [-inf, inf]
z: int = {3: {0: 0}, 4: {0: 1}, 5: {0: x}}[5][0]
# STATE: x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError
