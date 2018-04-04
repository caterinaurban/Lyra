# example: List[int] = [0, 1, 2]
value: int = input()

example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
key: str = "b"
example[key]: int = value
i: int = example["a"]

print(i)
