subject: str = input()
homeworks: int = int(input())
students: int = int(input())
for i in range(students):
    id: str = input()
    if id.isdigit():
       print("Student ID: " + id)
    else:
       raise ValueError("Invalid ID.")
    sum: float = 0
    max: float = 0
    for j in range(homeworks):
        grade: float = float(input())
        best: float = float(input())
        if grade < 0 or grade > best:
            raise ValueError
        sum: float = sum + grade
        max: float = max + best
    print("Average homework grades:")
    print(sum / max * 100.0)