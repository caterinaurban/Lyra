b: str = input()
c: str = input()

a: str = b + c

if (a == 'abc' or a == 'bcd') or a == 'ccc':
    pass
else:
    raise ValueError
