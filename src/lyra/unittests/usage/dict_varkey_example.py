
# INITIAL: example -> W; i -> W; key -> W; keys(example) -> W; len(example) -> N; len(key) -> N; value -> W; values(example) -> W
value: int = input()
# STATE: example -> W; i -> W; key -> W; keys(example) -> W; len(example) -> N; len(key) -> N; value -> U; values(example) -> W
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> U; i -> W; key -> W; keys(example) -> U; len(example) -> N; len(key) -> N; value -> U; values(example) -> U
key: str = "b"
# STATE: example -> U; i -> W; key -> U; keys(example) -> U; len(example) -> N; len(key) -> N; value -> U; values(example) -> U
example[key]: int = value
# STATE: example -> U; i -> W; key -> N; keys(example) -> U; len(example) -> N; len(key) -> N; value -> N; values(example) -> U
i: int = example["a"]
# STATE: example -> N; i -> U; key -> N; keys(example) -> N; len(example) -> N; len(key) -> N; value -> N; values(example) -> N
print(i)
# FINAL: example -> N; i -> N; key -> N; keys(example) -> N; len(example) -> N; len(key) -> N; value -> N; values(example) -> N
