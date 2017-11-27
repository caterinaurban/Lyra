
f = open('input2.txt', 'r')
first_line = f.readline()
lines = f.readlines()
f.close()

grades = []

for line in lines:
    fields = line.strip().split(",")
    if fields[1] == 'hw':
        for grade in fields[2:6]:
            grades.append(int(grade))
    else:
        grades.append(int(fields[2]))

for grade in grades:
    if grade < 1 or grade > 6:
        raise ValueError('Invalid grade!')

print('class average:', sum(grades) / len(grades))