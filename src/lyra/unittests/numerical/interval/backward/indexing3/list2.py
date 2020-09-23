
y: int = int(input())
# STATE: len(x) -> [0, inf]; x -> _@[-inf, inf]; y -> [0, 0]
x: List[int] = [y, 1, 2]
# STATE: len(x) -> [1, inf]; x -> 0@[0, 0], _@[-inf, inf]; y -> [-inf, inf]
if x[0] != 0:
    raise ValueError
