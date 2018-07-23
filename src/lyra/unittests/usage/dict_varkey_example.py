# INITIAL: example -> W, i -> W, key -> W, value -> W
value: int = input()
# STATE: example -> W, i -> W, key -> W, value -> U
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> U, i -> W, key -> W, value -> U
key: str = "b"
# STATE: example -> U, i -> W, key -> U, value -> U
example[key]: int = value
# STATE: example -> U, i -> W, key -> N, value -> N
i: int = example["a"]
# STATE: example -> N, i -> U, key -> N, value -> N
print(i)
# FINAL: example -> N, i -> N, key -> N, value -> N
