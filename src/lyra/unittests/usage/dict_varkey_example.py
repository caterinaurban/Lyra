# INITIAL: example -> W, i -> W, key -> W, len(key) -> N, value -> W
value: int = input()
# STATE: example -> W, i -> W, key -> W, len(key) -> N, value -> U
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> U, i -> W, key -> W, len(key) -> N, value -> U
key: str = "b"
# STATE: example -> U, i -> W, key -> U, len(key) -> N, value -> U
example[key]: int = value
# STATE: example -> U, i -> W, key -> N, len(key) -> N, value -> N
i: int = example["a"]
# STATE: example -> N, i -> U, key -> N, len(key) -> N, value -> N
print(i)
# FINAL: example -> N, i -> N, key -> N, len(key) -> N, value -> N
