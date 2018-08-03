subject: str = input()
number_of_students: int = int(input())
for i in range(number_of_students):
    student_name: str = input()
    homeworks: int = int(input())
    hw_grade_sum: float = 0
    max_grade_sum: float = 0
    for j in range(homeworks):
        max_hw_grade: float = float(input())
        student_hw_grade: float = float(input())
        if student_hw_grade < 0 or student_hw_grade > max_hw_grade:
            raise ValueError
        hw_grade_sum: float = hw_grade_sum + student_hw_grade
        max_grade_sum: float = max_grade_sum + max_hw_grade

    print("Student names:")
    print(student_name)
    print("Total homework grades:")
    print(hw_grade_sum)
    print("out of")
    print(max_hw_grade)
    max_test_grade: float = float(input())
    student_test_grade: float = float(input())
    if student_test_grade < 0 or student_test_grade > max_test_grade:
        raise ValueError
    print("Final test grade")
    print(student_test_grade)
    print("out of")
    print(max_test_grade)
