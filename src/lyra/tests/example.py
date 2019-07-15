value: int = input()

example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
key: str = "b"
example[key]: int = value
numbers: List[int] = [25, 12, 28]
print(numbers)

a: str = "a"

if a not in example.keys():
    raise ValueError

if 1 not in example.values():
    raise ValueError

i: int = example[a]
if i != 0:
    raise ValueError

