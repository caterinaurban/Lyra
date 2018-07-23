
# INITIAL: example -> W, i -> W, value -> W
value: int = input()
# STATE: example -> W, i -> W, value -> U
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> U, i -> W, value -> U
example["a"]: int = value
# STATE: example -> U, i -> W, value -> N
i: int = example["a"]
# STATE: example -> N, i -> U, value -> N
print(i)
# FINAL: example -> N, i -> N, value -> N
