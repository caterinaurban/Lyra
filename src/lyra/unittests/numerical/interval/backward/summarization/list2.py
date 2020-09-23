
y: int = int(input())
# STATE: len(x) -> [0, inf]; x -> [-inf, inf]; y -> [-inf, inf]
x: List[int] = [y, 1, 2]
# STATE: len(x) -> [1, inf]; x -> [-inf, inf]; y -> [-inf, inf]
if x[0] != 0:
    raise ValueError
