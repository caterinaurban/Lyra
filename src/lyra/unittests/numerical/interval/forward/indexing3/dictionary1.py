
value: int = 3
# STATE: example -> _@[-inf, inf]; i -> [-inf, inf]; keys(example) -> _@[-inf, inf]; len(example) -> [0, inf]; value -> [3, 3]; values(example) -> [-inf, inf]
example: Dict[str, int] = {'a': 0, 'b': 1, 'c': 2}
# STATE: example -> "a"@[0, 0], "b"@[1, 1], "c"@[2, 2], _@⊥; i -> [-inf, inf]; keys(example) -> 0@[-inf, inf], _@⊥; len(example) -> [3, 3]; value -> [3, 3]; values(example) -> [0, 2]
example['a']: int = value
# STATE: example -> "a"@[3, 3], "b"@[1, 1], "c"@[2, 2], _@⊥; i -> [-inf, inf]; keys(example) -> 0@[-inf, inf], _@⊥; len(example) -> [3, 3]; value -> [3, 3]; values(example) -> [1, 3]
i: int = example['a']
# STATE: example -> "a"@[3, 3], "b"@[1, 1], "c"@[2, 2], _@⊥; i -> [3, 3]; keys(example) -> 0@[-inf, inf], _@⊥; len(example) -> [3, 3]; value -> [3, 3]; values(example) -> [1, 3]
print(i)
