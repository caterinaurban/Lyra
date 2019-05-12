
grade2gpa: Dict[str, float] = { 'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0 }
students: int = int(input())
# STATE: students * [6:(⊤, [-inf, inf], ⊤), 7:(≠0, [-inf, inf], ⊤), 7.1 * 10:(⊤, [-inf, inf], ⊤)]
for _ in range(students):
    name: str = input()
    grades: int = int(input())
    gpa: float = 0.0
    for _ in range(grades):
        grade: str = input()
        gpa += grade2gpa[grade]
    result: float = gpa / grades
    print(result)
