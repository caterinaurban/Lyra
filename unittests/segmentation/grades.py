list_grades = list(map(int, input().split()))

count = 0

i = 1  # Bug A: should be 'i = 0'
# RESULT: count→⚫, g→⟂, i→⟂, list_grades→[{【[0,0]】} ⟂ ?{【+list_grades__len】}], list_grades__len→⟂
while i < len(list_grades):
    g = list_grades[i]
    if g >= 4:
        g += 1  # Bug B: should be 'count += 1'

    i += 1

print(count)
