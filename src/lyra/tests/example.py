grade2gpa: Dict[str, float] = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}

file: List[str] = input()
for line in file:
    data: List[str] = line.split()
    grades: int = int(data[1])
    gpa: float = 0.0
    for i in range(2, grades + 2):
        gpa += grade2gpa[data[i]]
    result: float = gpa/grades
    print(data[0])
    print(result)


