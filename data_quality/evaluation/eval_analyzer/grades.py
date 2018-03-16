# Analysis finds:
#[0 x [24:(Any, [-inf, inf])] with delimiter ';',
# 100 x [26:(Any, [-inf, inf]),
    # 0 x [27:((Any, [-inf, inf]),
        # [len(.ID=24) - len(.ID=27) + 0 <= 0, -len(.ID=24) + len(.ID=27) + 0 <= 0])] with delimiter ',',
    # 35:(Int, [-inf, inf])]]

# Manually
# len(1) == len(3)
# len(3) > 0
# [1: list[str], 100x[2:str, 3:list[float]], int]

# Difference.
# len(ID1) >= len(3) and len(ID1) >= len(ID3) instead of just len(ID1) == len(ID3)
# len(ID3) > 0 not found
# ID3 must be list of floats not detected

from typing import List

from data_quality.examples.homeworks.cis192.tadas412 import InvalidFormatException

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
    # len(input) > 0
    hw_grades: List[str] = input().split(",")
    # len(subjects) == len(hw_grades)
    # len(subjects) >= len(hw_grades)
    if len(subjects) < len(hw_grades):
        raise InvalidFormatException
    # len(subjects) <= len(hw_grades)
    if len(subjects) > len(hw_grades):
        raise InvalidFormatException
    hw_sum: float = 0
    for j in range(len(hw_grades)):
        hw_sum: float = hw_sum + float(hw_grades[j])
    # test_grade is int
    test_grade: int = int(input())
    student_names[i]: str = student_name
    # len(hw_grades) > 0
    hw_avgs[i]: float = hw_sum / len(hw_grades)
    test_grades[i]: int = test_grade

for i in range(len(student_names)):
    print("Student name:")
    print(student_names[i])
    print("Homework average:")
    print(hw_avgs[i])
    print("Test grade:")
    print(test_grades[i])
    print("")
