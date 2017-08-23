list_grades = list(map(int, input().split()))
list_compensate = list(map(int, input().split()))

# Total accumulated points
points = 0

i = 1
while i < len(list_grades):
    g = list_grades[i]
    diff = g - 40
    if diff >= 0:
        points += diff
    else:  # diff < 0
        c = list_compensate[i]
        if c != i:
            # compensate with grade at i
            list_grades[i] = list_grades[c]
            continue
        else:
            # count uncompensate unsatisfying grades double
            points += 2 * diff

    i += 1

if points >= 0:
    result = 1  # passed
else:
    result = -1  # failed

print(result)
