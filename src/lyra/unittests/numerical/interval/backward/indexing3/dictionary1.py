
example: Dict[str, int] = dict()
for i in range(3):
    example[i] = i
value: int = int(input())
# STATE: example -> _@[-inf, inf]; i -> [-inf, inf]; keys(example) -> _@[-inf, inf]; len(example) -> [0, inf]; value -> [3, 3]; values(example) -> [-inf, inf]
example[0]: int = value
# STATE: example -> 0@[3, 3], _@[-inf, inf]; i -> [-inf, inf]; keys(example) -> _@[-inf, inf]; len(example) -> [1, inf]; value -> [-inf, inf]; values(example) -> [-inf, inf]
i: int = example[0]
# STATE: example -> _@[-inf, inf]; i -> [3, 3]; keys(example) -> _@[-inf, inf]; len(example) -> [0, inf]; value -> [-inf, inf]; values(example) -> [-inf, inf]
if i != 3:
    raise ValueError
