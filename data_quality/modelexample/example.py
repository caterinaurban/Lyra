
f = open('input.txt', 'r')
first_line = f.readline()
lines = f.readlines()
f.close()

names = []
grades = []

for line in lines:
    fields = line.strip().split(",")
    names.append(fields[0])
    curr_grades = []
    if len(fields) == 5:
        for grade in fields[1:5]:
            curr_grades.append(int(grade))
    else:
        for i in range(4):
            curr_average = (int(fields[i+1]) + int(fields[i+5])) / 2
            curr_grades.append(curr_average)
    grades.append(curr_grades)

print()
print('averages:')

for i in range(len(names)):
    average_grade = sum(grades[i]) / len(grades[i])
    print(names[i], average_grade)