# INITIAL: value -> Dead, example -> Dead, key -> Dead, i -> Dead
value: int = input()
# STATE: value -> Live, example -> Dead, key -> Dead, i -> Dead
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: value -> Live, example -> Live, key -> Dead, i -> Dead
key: str = "b"
# STATE: value -> Live, example -> Live, key -> Live, i -> Dead
example[key]: int = value
# STATE: value -> Dead, example -> Live, key -> Dead, i -> Dead
i: int = example["a"]
# STATE: value -> Dead, example -> Dead, key -> Dead, i -> Live
print(i)
# FINAL: value -> Dead, example -> Dead, key -> Dead, i -> Dead
