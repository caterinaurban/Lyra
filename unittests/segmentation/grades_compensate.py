list_grades = list(map(int, input().split()))
list_compensate = list(map(int, input().split()))

# Total accumulated points
points = 0

i = 1  # BUG: should be i = 0
n = len(list_grades)
while i < n - 1:  # BUG: should be i < n
    g = list_grades[i]

    diff = g - 40
    if diff >= 0:  # satisfying grade
        points += diff
    else:  # diff < 0, unsatisfying grade
        c = list_compensate[n]  # BUG: should be list_compensate[c]
        if c != i:
            # compensate with grade at i
            list_grades[i] = list_grades[c]
            continue
        else:
            # count unsatisfying grades double
            points += 2 * diff  # BUG: should be +=

    i += 1

if points >= 0:
    result = 1  # passed
else:
    result = -1  # failed

print(result)
