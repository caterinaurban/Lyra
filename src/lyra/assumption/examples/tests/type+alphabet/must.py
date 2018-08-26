# 3:(String, ⊤, ⊤, ({'c'}, {'a', 'b', 'c', 'd'}))
# INITIAL: 3:(String, ({'c'}, {'a', 'b', 'c', 'd'}))
a: str = input()
if a == 'abc' or a == 'bcd' or a == 'ccc':
    pass
else:
    raise ValueError
