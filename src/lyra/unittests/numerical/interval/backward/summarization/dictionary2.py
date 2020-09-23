
Y: int = int(input())
Z: int = int(input())
# STATE: Y -> [-inf, inf]; Z -> [-inf, inf]; keys(x) -> [-inf, inf]; len(x) -> [0, inf]; values(x) -> [-inf, inf]; x -> [-inf, inf]
x: Dict[str, int] = {'a': Y, 'b': Z}
# STATE: Y -> [-inf, inf]; Z -> [-inf, inf]; keys(x) -> [-inf, inf]; len(x) -> [1, inf]; values(x) -> [-inf, inf]; x -> [-inf, inf]
if x['b'] != 0 or x['a'] < 0:
    raise ValueError
