
# INITIAL: example -> Dead, i -> Dead, value -> Dead
value: int = int(input())
# STATE: example -> Dead, i -> Dead, value -> Live
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
# STATE: example -> Live, i -> Dead, value -> Live
example["a"]: int = value
# STATE: example -> Live, i -> Dead, value -> Dead
i: int = example["a"]
# STATE: example -> Dead, i -> Live, value -> Dead
print(i)
# FINAL: example -> Dead, i -> Dead, value -> Dead
