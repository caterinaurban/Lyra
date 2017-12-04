number_grades: str = input()
kind_of_grade: int = int(input())
in1: str = input()
in2: str = input()

grade1: float = 0
grade2: float = 0

if kind_of_grade == 1:
    grade1: float = 7 - int(in1)
else:
    grade1: float = int(in1)

if grade1 < 1 or grade1 > 6:
    raise ValueError('Invalid grade!')

if kind_of_grade == 1:
    grade2: float = 7 - int(in2)
else:
    grade2: float = int(in2)

if grade2 < 1 or grade2 > 6:
    raise ValueError('Invalid grade!')

print('grade:')
print((grade1 + grade2) / int(number_grades))
