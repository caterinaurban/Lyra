a: List[str] = input().split()
b: List[str] = input().split()

if not (len(a) == len(b)):
    raise ValueError

for i in range(len(a)):
    if a[i] != b[i]:
        raise ValueError
