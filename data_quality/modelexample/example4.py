
data = []
for line in open('input4.txt', 'r'):
    data.append(line.strip().split(","))

grades_2015 = []
grades_2016 = []
names = []
for fields in data:
    if fields[1] == '2015':
        grade = (int(fields[2]) + int(fields[3])) / 2
        grades_2015.append(grade)
        names.append(fields[0])
    else:
        grades_2016.append(int(fields[2]))

for i in range(len(grades_2015)):
    print(names[i], 'has an average grade of', (grades_2015[i] + grades_2016[i]) / 2)

