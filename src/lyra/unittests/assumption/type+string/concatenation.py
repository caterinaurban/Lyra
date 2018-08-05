
# INITIAL: 3:(String, (∅, {'a', 'b', 'c', 'd'})), 5:(String, (∅, {'a', 'b', 'c', 'd'}))
b: str = input()
# STATE: 5:(String, (∅, {'a', 'b', 'c', 'd'}))
c: str = input()
a: str = b + c
if a == 'abc' or a == 'bcd' or a == 'ccc':
    pass
else:
    raise ValueError
