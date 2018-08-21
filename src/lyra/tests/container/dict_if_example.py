
key: str = input()
example: Dict[str, int] = {"a": 0, "b": 1, "c": 2}
thresh: int = 1
if (example[key] > thresh):
    ret: bool = True
else:
    ret: bool = False

print(ret)
