
# INITIAL: value -> W, example -> W, i -> W
value: int = input()
# STATE: value -> U, example -> W, i -> W
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: value -> U, example -> U, i -> W
example["a"]: int = value
# STATE: value -> N, example -> U, i -> W
i: int = example["a"]
# STATE: value -> N, example -> N, i -> U
print(i)
# FINAL: value -> N, example -> N, i -> N
