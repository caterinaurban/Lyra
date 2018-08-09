
# INITIAL: 3:(String, ({'a', 'b', 'c'}, {'a', 'b', 'c'})), 5:(String, ({'a', 'b', 'c'}, {'a', 'b', 'c'})), 7:(String, (∅, ∅))
a: str = input()
# STATE: 5:(String, ({'a', 'b', 'c'}, {'a', 'b', 'c'})), 7:(String, (∅, ∅))
b: str = input()
# STATE: 7:(String, (∅, ∅))
c: str = input()
# STATE: ε
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
# FINAL: ε
