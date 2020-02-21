# INITIAL: example -> Dead; i -> Dead; key -> Dead; len(example) -> Dead; len(key) -> Dead; value -> Dead
value: int = int(input())
# STATE: example -> Dead; i -> Dead; key -> Dead; len(example) -> Dead; len(key) -> Dead; value -> Live
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> Live; i -> Dead; key -> Dead; len(example) -> Dead; len(key) -> Dead; value -> Live
key: str = "b"
# STATE: example -> Live; i -> Dead; key -> Live; len(example) -> Dead; len(key) -> Dead; value -> Live
example[key]: int = value
# STATE: example -> Live; i -> Dead; key -> Dead; len(example) -> Dead; len(key) -> Dead; value -> Dead
i: int = example["a"]
# STATE: example -> Dead; i -> Live; key -> Dead; len(example) -> Dead; len(key) -> Dead; value -> Dead
print(i)
# FINAL: example -> Dead; i -> Dead; key -> Dead; len(example) -> Dead; len(key) -> Dead; value -> Dead
