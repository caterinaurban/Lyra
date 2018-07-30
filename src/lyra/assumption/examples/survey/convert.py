weight: int = int(input())
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
