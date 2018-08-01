a: str = input()
b: str = input()
c: str = input()


if a == b + c:
    pass
else:
    raise ValueError

if a == 'abc':
    pass
else:
    raise ValueError

if c == '':
    pass
else:
    raise ValueError

if b == 'abc':
    pass
else:
    raise ValueError