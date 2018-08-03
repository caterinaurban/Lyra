# # RESULT 2:(String, T, T), 3:(Integer, T, T), 4:(Integer, T, T), 4.1 * [6:(String, T, T), 3.1 * [10:(Float, OCT( +10.1 + 0.0 >= 0), T), 11:(Float, OCT( +11.1 + 0.0 >= 0, -11.1 + 10.1 + 0.0 >= 0, +11.1 + 10.1 + 0.0 >= 0, +10.1 + 0.0 >= 0), T)], 23:(Float, T, T), 24:(Float, T, T)]
subject: str = input()
homeworks: int = int(input())
number_of_students: int = int(input())
for i in range(number_of_students):
    student_id: str = input()
    hw_grade_sum: float = 0
    max_grade_sum: float = 0
    for j in range(homeworks):
        max_hw_grade: float = float(input())
        student_hw_grade: float = float(input())
        if student_hw_grade < 0 or student_hw_grade > max_hw_grade:
            raise ValueError
        hw_grade_sum: float = hw_grade_sum + student_hw_grade
        max_grade_sum: float = max_grade_sum + max_hw_grade

    print("Student ID:")
    print(student_id)
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
