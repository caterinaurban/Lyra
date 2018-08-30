# 3:(String, ⊤, ⊤, (∅, Σ)), 5 * 5:(String, ⊤, ⊤, ({'a', 'b', 'c'}, {'a', 'b', 'c'})),
# 10:(String, ⊤, ⊤, (∅, Σ)) INITIAL: 3:(String, [-inf, inf]), 5 * 5:(String, [-inf, inf]),
# 7:(String, [-inf, inf])
x: str = input()
for i in range(5):
    y: str = input()
    if y == "abc":
        print(y)
    else:
        raise ValueError
z: str = input()
