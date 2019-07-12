value: int = input()

example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
key: str = "b"
example[key]: int = value
numbers: List[int] = [25, 12, 28]
print(numbers)

a: str = "a"
i: int = example[a]
if i != 0:
    raise ValueError

