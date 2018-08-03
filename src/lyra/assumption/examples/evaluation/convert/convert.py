N: int = int(input())
if N == 0:
    raise ValueError
for i in range(N):
    item_name: str = input()
    weight: int = int(input())
    if weight <= 0:
        raise ValueError
    unit: str = input()
    if (unit == 'pounds' or unit == 'lb') or (unit == 'lbs'):
        print(weight * 453.592 * 1e-3)
    elif (unit == 'ounces' or unit == 'oz') or (unit == 'oz.'):
        print(weight * 28.35 * 1e-3)
    elif (unit == 'grams' or unit == 'gms') or (unit == 'g'):
        print(weight * 1e-3)
    elif (unit == 'kilograms' or unit == 'kilo') or unit == 'kg':
        print(weight)
    else:
        raise ValueError
    print("item: ")
    print(item_name)
    print(", ")
    print("weight: ")
    print(weight)
    print("kg")
