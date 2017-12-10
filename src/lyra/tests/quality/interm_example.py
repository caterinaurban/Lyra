
number_grades_in: str = input()
number_grades: int = int(number_grades_in)

if number_grades != 2:
    raise ValueError("Two grades are expected!")

kind_of_grade: int = int(input())  # 1 = Macedonia, 2 = Switzerland
in1: str = input()
in2: str = input()

grade1: float = 0
grade2: float = 0

if kind_of_grade == 1:
    grade1: float = int(in1) - 4
    grade2: float = int(in2) - 4
else:
    grade1: float = int(in1)
    grade2: float = int(in2)

if (grade1 < 1 or grade1 > 6) or (grade2 < 1 or grade2 > 6):
    raise ValueError('Invalid grade!')

print((grade1 + grade2) / 2)