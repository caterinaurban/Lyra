
# INITIAL: value -> Dead, example -> Dead, i -> Dead
value: int = input()
# STATE: value -> Live, example -> Dead, i -> Dead
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: value -> Live, example -> Live, i -> Dead
example["a"]: int = value
# STATE: value -> Dead, example -> Live, i -> Dead
i: int = example["a"]
# STATE: value -> Dead, example -> Dead, i -> Live
print(i)
# FINAL: value -> Dead, example -> Dead, i -> Dead
