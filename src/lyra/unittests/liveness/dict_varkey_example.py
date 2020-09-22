# INITIAL: example -> Dead; i -> Dead; key -> Dead; keys(example) -> Dead; len(example) -> [0, inf]; len(key) -> [0, inf]; value -> Dead; values(example) -> Dead
value: int = int(input())
# STATE: example -> Dead; i -> Dead; key -> Dead; keys(example) -> Dead; len(example) -> [0, inf]; len(key) -> [0, inf]; value -> Live; values(example) -> Dead
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> Live; i -> Dead; key -> Dead; keys(example) -> Live; len(example) -> [0, inf]; len(key) -> [0, inf]; value -> Live; values(example) -> Live
key: str = "b"
# STATE: example -> Live; i -> Dead; key -> Live; keys(example) -> Live; len(example) -> [0, inf]; len(key) -> [0, inf]; value -> Live; values(example) -> Live
example[key]: int = value
# STATE: example -> Live; i -> Dead; key -> Dead; keys(example) -> Live; len(example) -> [0, inf]; len(key) -> [0, inf]; value -> Dead; values(example) -> Live
i: int = example["a"]
# STATE: example -> Dead; i -> Live; key -> Dead; keys(example) -> Dead; len(example) -> [0, inf]; len(key) -> [0, inf]; value -> Dead; values(example) -> Dead
print(i)
# FINAL: example -> Dead; i -> Dead; key -> Dead; keys(example) -> Dead; len(example) -> [0, inf]; len(key) -> [0, inf]; value -> Dead; values(example) -> Dead
