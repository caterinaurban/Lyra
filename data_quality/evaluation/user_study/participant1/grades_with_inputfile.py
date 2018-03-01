from typing import List

import sys

from data_quality.examples.homeworks.cis192.tadas412 import InvalidFormatException

sys.stdin = open('grades.in', 'r')

student_names: List[str] = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                            "", "", "", "", "", "", "", "", "", ""]
hw_avgs: List[float] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
test_grades: List[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

subjects: List[str] = input().split(";")
for i in range(100):
    student_name: str = input()
    hw_grades: List[str] = input().split(",")
    if len(subjects) < len(hw_grades):
        raise InvalidFormatException
    if len(subjects) > len(hw_grades):
        raise InvalidFormatException
    hw_sum: float = 0
    for j in range(len(hw_grades)):
        hw_sum: float = hw_sum + float(hw_grades[j])
    test_grade: int = int(input())
    student_names[i]: str = student_name
    hw_avgs[i]: float = hw_sum / len(hw_grades)
    test_grades[i]: int = (test_grade + hw_avgs[i]) / 2

for i in range(len(student_names)):
    print("Student name:")
    print(student_names[i])
    print("Homework average:")
    print(hw_avgs[i])
    print("Test grade:")
    print(test_grades[i])
    print("")
