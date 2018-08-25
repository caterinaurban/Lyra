x: str = input()
y: str = input()

if not x.islower():
    pass
else:
    raise ValueError

if not x.isalpha() or not y.isalnum():
    raise ValueError