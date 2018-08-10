
# INITIAL: 3:(String, ({'b', 'c'}, {'a', 'b', 'c', 'd'}))
a: str = input()
if a == 'abc':
    print(a)
elif a == 'bcd':
    print(a)
else:
    raise ValueError
