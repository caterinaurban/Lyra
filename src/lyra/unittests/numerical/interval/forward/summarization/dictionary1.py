
value: int = 3
# STATE: example -> [-inf, inf]; i -> [-inf, inf]; keys(example) -> [-inf, inf]; len(example) -> [0, inf]; value -> [3, 3]; values(example) -> [-inf, inf]
example: Dict[str, int] = {'a': 0, 'b': 1, 'c': 2}
# STATE: example -> [-inf, inf]; i -> [-inf, inf]; keys(example) -> [-inf, inf]; len(example) -> [3, 3]; value -> [3, 3]; values(example) -> [0, 2]
example['a']: int = value
# STATE: example -> [-inf, inf]; i -> [-inf, inf]; keys(example) -> [-inf, inf]; len(example) -> [3, 4]; value -> [3, 3]; values(example) -> [0, 3]
i: int = example['a']
# STATE: example -> [-inf, inf]; i -> [0, 3]; keys(example) -> [-inf, inf]; len(example) -> [3, 4]; value -> [3, 3]; values(example) -> [0, 3]
print(i)
