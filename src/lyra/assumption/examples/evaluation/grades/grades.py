# PARSED RESULT 5:(String, ⊤, T, (∅, Σ)), 6:(Integer, ⊤, T, (∅, Σ)), 7:(Integer, ⊤, T, (∅, Σ)), 7.1 * [9:(String, ⊤, T, (∅, Σ)), 6.1 * [13:(Float, ⊤, OCT( +13.1 + 0.0 >= 0), (∅, Σ)), 14:(Float, ≥0, OCT( +14.1 + 0.0 >= 0, -14.1 + 13.1 + 0.0 >= 0, +14.1 + 13.1 + 0.0 >= 0, +13.1 + 0.0 >= 0), (∅, Σ))], 26:(Float, ⊤, OCT( +26.1 + 0.0 >= 0), (∅, Σ)), 27:(Float, ≥0, OCT( +27.1 + 0.0 >= 0, -27.1 + 26.1 + 0.0 >= 0, +27.1 + 26.1 + 0.0 >= 0, +26.1 + 0.0 >= 0), (∅, Σ))]
import sys
sys.stdin = open('grades.in', 'r')
subject: str = input()
homeworks: int = int(input())
number_of_students: int = int(input())
for i in range(number_of_students):
    student_id: str = input()
    hw_grade_sum: float = 0
    max_grade_sum: float = 0
    for j in range(homeworks):
        student_hw_grade: float = float(input())
        max_hw_grade: float = float(input())
        if student_hw_grade < 0 or student_hw_grade > max_hw_grade:
            raise ValueError
        hw_grade_sum: float = hw_grade_sum + student_hw_grade
        max_grade_sum: float = max_grade_sum + max_hw_grade

    avg_homework: float = hw_grade_sum / max_grade_sum * 100.0;
    print("Student ID:")
    print(student_id)
    print("Average homework grade:")
    print(avg_homework)
    student_test_grade: float = float(input())
    max_test_grade: float = float(input())
    if student_test_grade < 0 or student_test_grade > max_test_grade:
        raise ValueError
    final_grade: float = student_hw_grade / max_test_grade * 100.0
    print("Final test grade:")
    print(final_grade)