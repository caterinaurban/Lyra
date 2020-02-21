
# INITIAL: example -> Dead; i -> Dead; len(example) -> Dead; value -> Dead
value: int = int(input())
# STATE: example -> Dead; i -> Dead; len(example) -> Dead; value -> Live
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> Live; i -> Dead; len(example) -> Dead; value -> Live
example["a"]: int = value
# STATE: example -> Live; i -> Dead; len(example) -> Dead; value -> Dead
i: int = example["a"]
# STATE: example -> Dead; i -> Live; len(example) -> Dead; value -> Dead
print(i)
# FINAL: example -> Dead; i -> Dead; len(example) -> Dead; value -> Dead
