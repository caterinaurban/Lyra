# https://cambridgespark.com/content/tutorials/interactively-analyse-100GB-of-JSON-data-with-Spark/index.html
# RESULT 2:(Integer, T, T), 2.1 * [6:(String, T, T), 7:(Integer, OCT( +7.1 - 1.0 >= 0), T), 10:(String, T, (set(), {'i', '.', 'z', 'm', 'e', 'd', 'n', 's', 'g', 'o', 'r', 'a', 'u', 'l', 'c', 'b', 'p', 'k'})), ★]
import sys
sys.stdin = open('convert.in', 'r')
number_of_items: int = int(input())
if number_of_items == 0:
    raise ValueError
for i in range(number_of_items):
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
    print("Item: ")
    print(item_name)
    print(", ")
    print("weight: ")
    print(weight)
    print("kg")
