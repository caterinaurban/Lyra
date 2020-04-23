
example: List[int] = list()
for i in range(3):
    example.append(i)
value: int = int(input())
# STATE: example -> _@[-inf, inf]; i -> [-inf, inf]; len(example) -> [3, inf]; value -> [3, 3]
example[2]: int = value
# STATE: example -> 2@[3, 3], _@[-inf, inf]; i -> [-inf, inf]; len(example) -> [3, inf]; value -> [-inf, inf]
i: int = example[2]
# STATE: example -> _@[-inf, inf]; i -> [3, 3]; len(example) -> [0, inf]; value -> [-inf, inf]
if i != 3:
    raise ValueError
