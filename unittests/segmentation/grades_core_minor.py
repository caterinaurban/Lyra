list_core_grades = list(map(int, input().split()))
list_minor_grades = list(map(int, input().split()))

# Total accumulated points
points = 0
total_points = 0
# RESULT: diff→⫱, g→⫱, i→⫱, points→⫱, result→⫱, total_points→⚫, list_core_grades→[{【[0,0]】} ⟂ ?{【+list_core_grades__len】}], list_minor_grades→[{【[0,0]】} ⟂ ?{【[1,1]】} ⚫ {【[2,2]】} ⚫ {【[3,3]】} ⚫ {【[4,4]】} ⚫ ?{【+list_minor_grades__len】}], list_core_grades__len→⚫, list_minor_grades__len→⟂
# CALCULATE CORE SUBJECTS POINTS
i = 0
while i < len(list_core_grades):
    g = list_core_grades[i]

    diff = g - 4
    if diff >= 0:  # passing grade
        points += diff
    else:  # diff < 0
        points += 2 * diff

    i += 1

# Bug A: missing 'total_points += points'
points = 0

# CALCULATE MINOR SUBJECTS POINTS
i = 1  # Bug B: should be 'i = 0'
while i < len(list_core_grades) - 1:  # Bug C: should be <=
    g = list_minor_grades[i]

    diff = g - 4
    points += diff

    i += 1

total_points += points

if total_points >= 0:
    result = 1  # passed
else:
    result = -1  # failed

print(result)
