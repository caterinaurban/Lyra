# 3:(Integer, ≠0, ⊤, (∅, Σ)), 3.1 * [7:(String, ⊤, ⊤, (∅, Σ)), 8:(Integer, >0, OCT(8.1 - 1.0 >=
# 0), (∅, Σ)), 11:(String, ⊤, ⊤, (∅, {'.', 'a', 'b', 'c', 'd', 'e', 'g', 'i', 'k', 'l', 'm',
# 'n', 'o', 'p', 'r', 's', 'u', 'z'}))]

items: int = int(input())
if items == 0:
    raise ValueError
for i in range(items):
    name: str = input()
    weight: float = int(input())
    if weight <= 0:
        raise ValueError
    unit: str = input()
    if unit == 'pounds' or unit == 'lb' or unit == 'lbs':
        weight: float = weight * 453.592 * 1e-3
    elif unit == 'ounces' or unit == 'oz' or unit == 'oz.':
        weight: float = weight * 28.35 * 1e-3
    elif unit == 'grams' or unit == 'gms' or unit == 'g':
        weight: float = weight * 1e-3
    elif unit == 'kilograms' or unit == 'kilo' or unit == 'kg':
        pass
    else:
        raise ValueError
    print("Item: " + name)
    print("weight:")
    print(weight)
    print("kg")
# FINAL: ε
# TOTAL ASSUMPTIONS:
# SOUND ASSUMPTIONS:
# IMPRECISIONS:
# LINE        DOMAIN      COMMENT
