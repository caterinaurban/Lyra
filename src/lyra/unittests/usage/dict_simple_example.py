
# INITIAL: example -> W, i -> W, len(example) -> N, value -> W
value: int = input()
# STATE: example -> W, i -> W, len(example) -> N, value -> U
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> U, i -> W, len(example) -> N, value -> U
example["a"]: int = value
# STATE: example -> U, i -> W, len(example) -> N, value -> N
i: int = example["a"]
# STATE: example -> N, i -> U, len(example) -> N, value -> N
print(i)
# FINAL: example -> N, i -> N, len(example) -> N, value -> N
