# INITIAL: value -> W, example -> W, key -> W, i -> W
value: int = input()
# STATE: value -> U, example -> W, key -> W, i -> W
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: value -> U, example -> U, key -> W, i -> W
key: str = "b"
# STATE: value -> U, example -> U, key -> U, i -> W
example[key]: int = value
# STATE: value -> N, example -> U, key -> N, i -> W
i: int = example["a"]
# STATE: value -> N, example -> N, key -> N, i -> U
print(i)
# FINAL: value -> N, example -> N, key -> N, i -> N
