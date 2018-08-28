# 2:(Integer, ⊤, ⊤, (∅, Σ)), 3:(Integer, ⊤, ⊤, (∅, Σ)), 4:(Integer, ⊤, ⊤, (∅, Σ)), 10 * [7:(
# Float, ≥0, OCT(7.1 >= 0,7.1 >= 4.1), (∅, Σ)), 11:(Float, ⊤, ⊤, (∅, Σ))]
weight_per_day1: int = int(input())
weight_per_day2: int = int(input())
day_string: str = input()
day: int = int(day_string)
for i in range(10):
    other_day: float = float(input())
    if other_day < 0 or other_day < day:
        raise ValueError
    if other_day > 2:
        food: float = int(input())
    else:
        food: float = float(input())
    print(food)

if day == 1:
    print(weight_per_day1)
else:
    print(weight_per_day2)

# TOTAL ASSUMPTIONS:
# SOUND ASSUMPTIONS:
# IMPRECISIONS:
# LINE        DOMAIN      COMMENT
