list_core_grades = list(map(int, input().split()))
list_minor_grades = list(map(int, input().split()))

# Total accumulated points
core_points = 0
minor_points = 0
total_points = 0

# CALCULATE CORE SUBJECTS POINTS
i = 1  # BUG: should be i = 0
while i < len(list_core_grades) - 1:  # BUG: should be i <= n
    g = list_core_grades[i]

    diff = g - 40
    if diff >= 0:  # satisfying grade
        core_points += diff
    else:  # diff < 0, unsatisfying grade
        core_points += 2 * diff  # BUG: should be +=

    i += 1

#total_points += core_points  # BUG: missing

# CALCULATE MINOR SUBJECTS POINTS
i = 1  # BUG: missing
while i < len(list_core_grades) - 1:  # BUG: should be i <= n
    g = list_minor_grades[i]

    diff = g - 40
    minor_points += diff

    i += 1

total_points += minor_points

if total_points >= 0:
    result = 1  # passed
else:
    result = -1  # failed

print(result)
