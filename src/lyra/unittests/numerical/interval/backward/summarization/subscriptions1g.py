
x: int = int(input())
# STATE: d -> [-inf, inf]; keys(d) -> [-inf, inf]; len(d) -> [0, inf]; values(d) -> [-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
d: Dict[int, int] = {3: {0: 0}, 4: {0: 1}, 5: {0: x}}[5]
# STATE: d -> [-inf, inf]; keys(d) -> [-inf, inf]; len(d) -> [1, inf]; values(d) -> [-inf, inf]; x -> [-inf, inf]; z -> [-inf, inf]
z: int = d[0]
# STATE: d -> [-inf, inf]; keys(d) -> [-inf, inf]; len(d) -> [0, inf]; values(d) -> [-inf, inf]; x -> [-inf, inf]; z -> [2, 2]
if z != 2:
    raise ValueError