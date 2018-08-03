
# INITIAL: 3:(Integer, [-inf, inf], (∅, Σ)), 3.1 * [7:(String, [-inf, inf], (∅, Σ)), 8:(Integer, [1, inf], (∅, Σ)), 11:(String, [-inf, inf], (∅, {'.', 'a', 'b', 'c', 'd', 'e', 'g', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 'u', 'z'}))]
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
