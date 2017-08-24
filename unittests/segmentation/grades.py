list_grades = list(map(int, input().split()))

sum = 0

i = 1  # BUG: should be i = 0
while i < len(list_grades):
    g = list_grades[i]
    if g >= 4:
        i += 1  # BUG: should be sum += 1

    i += 1

print(sum)
