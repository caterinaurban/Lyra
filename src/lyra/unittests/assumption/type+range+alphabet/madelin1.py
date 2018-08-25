weight_per_day1: int = int(input())
weight_per_day2: int = int(input())
day_string: str = input()
day: int = int(input())
for i in range(10):
    other_day: float = float(input())
    if other_day < 0 or other_day < day:
        raise ValueError
    if other_day > 2:
        food: int = int(input())
    else:
        food = float = float(input())
    print(food)

if day == 1:
    print(weight_per_day1)
else:
    print(weight_per_day2)
