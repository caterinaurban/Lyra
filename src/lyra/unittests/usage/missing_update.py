x1: int = int(input())  # x1 unused
x2: int = int(input())
x3: int = int(input())

# RESULT: x1 -> N; x2 -> U; x3 -> U; asc -> O; temp -> O

asc: bool = True
if x1 <= x2:
    temp: bool = False
else:
    temp: bool = True

# BUG, missing update on asc

if x2 <= x3:
    temp: bool = False
else:
    temp: bool = True

asc: bool = asc and temp

print(asc)
