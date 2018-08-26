# ASSUMPTIONS: 3:(String, ⊤, ⊤, (∅, {'#', '.'}))
# INITIAL: 3:(String, (∅, {'#', '.'}))
sep: str = input()
if sep != '.' and sep != '#':
    raise ValueError
