
# INITIAL: example -> W; i -> W; keys(example) -> W; len(example) -> N; value -> W; values(example) -> W
value: int = input()
# STATE: example -> W; i -> W; keys(example) -> W; len(example) -> N; value -> U; values(example) -> W
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> U; i -> W; keys(example) -> U; len(example) -> N; value -> U; values(example) -> U
example["a"]: int = value
# STATE: example -> U; i -> W; keys(example) -> U; len(example) -> N; value -> N; values(example) -> U
i: int = example["a"]
# STATE: example -> N; i -> U; keys(example) -> N; len(example) -> N; value -> N; values(example) -> N
print(i)
# FINAL: example -> N; i -> N; keys(example) -> N; len(example) -> N; value -> N; values(example) -> N
