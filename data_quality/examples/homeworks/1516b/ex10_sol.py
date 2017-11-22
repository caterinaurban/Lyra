import numpy
from scipy import misc


def extract_from_file(filename):
    f = open(filename, 'r')
    first_line = f.readline()
    lines = f.readlines()
    f.close()

    student_names = []
    hw_grades = []
    test_grades = []

    for line in lines:
        fields = line.strip().split(",")
        # MAD: len(fields) >= 1
        student_names.append(fields[0])
        cur_hw_grades = []
        # MAD: fields[1:-1] must be integer
        for grade in fields[1:-1]:
            # MAD: grade must be integer
            cur_hw_grades.append(int(grade))
        hw_grades.append(cur_hw_grades)
        # MAD: len(fields) >= 1
        # MAD: last elements of fields must be int
        test_grades.append(int(fields[-1]))
    
    return numpy.array(student_names), numpy.array(hw_grades), numpy.array(test_grades)
