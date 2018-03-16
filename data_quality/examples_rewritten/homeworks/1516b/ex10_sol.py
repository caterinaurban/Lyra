
f = open(filename, 'r')
first_line = f.readline()
lines = f.readlines()
f.close()

student_names = []
hw_grades = []
test_grades = []

for line in lines:
    fields = line.strip().split(",")
    student_names.append(fields[0])
    cur_hw_grades = []
    for grade in fields[1:-1]:
        cur_hw_grades.append(int(grade))
    hw_grades.append(cur_hw_grades)
    test_grades.append(int(fields[-1]))

print(student_names)  # print instead of return
print(hw_grades)
print(test_grades)
