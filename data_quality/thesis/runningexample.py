from typing import List

weight_per_day: List[str] = input().split(';')
day_string: str = input()
day: int = int(day_string)
print(weight_per_day[day])
for i in range(10):
    other_day: float = float(input())
    if other_day < 0:
        raise ValueError
    if other_day < day:
        raise ValueError
    if other_day > 2:
        food: float = int(input())
    else:
        food: float = float(input())
    print(food)
if day == 1:
    print(weight_per_day[2])
else:
    print(weight_per_day[3])