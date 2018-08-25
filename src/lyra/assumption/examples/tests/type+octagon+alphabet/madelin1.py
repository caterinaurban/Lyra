# 1:(Integer, ⊤, T, (∅, Σ)), 2:(Integer, ⊤, T, (∅, Σ)), 3:(Integer, ⊤, T, (∅, Σ)), 10 * [6:(Float, ≥0, OCT(6.1 >= 0), (∅, Σ)), 10:(Float, ⊤, T, (∅, Σ))]
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