
data = []
for line in open('input3.txt', 'r'):
    data.append(line.strip().split(","))

grades = []
for fields in data:
    if fields[1] == 'midterms':
        grade = (int(fields[2]) + 2 * int(fields[3])) / 3
        grades.append(grade)
    else:
        grades.append(int(fields[2]))

for grade in grades:
    if grade < 1 or grade > 6:
        raise ValueError('Invalid grade!')

print('class average:', sum(grades) / len(grades))