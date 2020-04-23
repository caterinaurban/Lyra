
example: Dict[str, int] = dict()
for i in range(3):
    example[i] = i
value: int = int(input())
# STATE: example -> [-inf, inf]; i -> [-inf, inf]; keys(example) -> [-inf, inf]; len(example) -> [0, inf]; value -> [-inf, inf]; values(example) -> [-inf, inf]
example[0]: int = value
# STATE: example -> [-inf, inf]; i -> [-inf, inf]; keys(example) -> [-inf, inf]; len(example) -> [1, inf]; value -> [-inf, inf]; values(example) -> [-inf, inf]
i: int = example[0]
# STATE: example -> [-inf, inf]; i -> [3, 3]; keys(example) -> [-inf, inf]; len(example) -> [0, inf]; value -> [-inf, inf]; values(example) -> [-inf, inf]
if i != 3:
    raise ValueError
