subject: str = input()
homeworks: int = int(input())
students: int = int(input())
for i in range(students):
    id: str = input()
    sum: float = 0
    max: float = 0
    for j in range(homeworks):
        best: float = float(input())
        grade: float = float(input())
        if grade < 0 or grade > best:
            raise ValueError
        sum: float = sum + grade
        max: float = max + best
    if id.isdigit():
        print("Student ID: " + id)
    else:
        raise ValueError("Invalid ID.")
    print("Average homework grades:")
    print(sum / max * 100.0)
    best: float = float(input())
    grade: float = float(input())
    if grade < 0 or grade > best:
        raise ValueError
    print("Final test grade:")
    print(grade / best * 100.0)
# FINAL: ε
