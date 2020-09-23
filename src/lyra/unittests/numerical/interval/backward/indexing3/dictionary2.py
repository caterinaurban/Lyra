
Y: int = int(input())
Z: int = int(input())
# STATE: Y -> [0, inf]; Z -> [0, 0]; keys(x) -> _@[-inf, inf]; len(x) -> [0, inf]; values(x) -> [-inf, inf]; x -> _@[-inf, inf]
x: Dict[str, int] = {'a': Y, 'b': Z}
# STATE: Y -> [-inf, inf]; Z -> [-inf, inf]; keys(x) -> _@[-inf, inf]; len(x) -> [1, inf]; values(x) -> [-inf, inf]; x -> "a"@[0, inf], "b"@[0, 0], _@[-inf, inf]
if x['b'] != 0 or x['a'] < 0:
    raise ValueError
