
# INITIAL: 3:(String, [-inf, inf], (∅, Σ)), 4:(Integer, [-inf, inf], (∅, Σ)), 5:(Integer, [-inf, inf], (∅, Σ)), 5.1 * [8:(String, [-inf, inf], (∅, Σ)), 4.1 * [12:(Float, [-inf, inf], (∅, Σ)), 13:(Float, [0, inf], (∅, Σ))], 24:(Float, [-inf, inf], (∅, Σ)), 25:(Float, [0, inf], (∅, Σ))]
subject: str = input()
homeworks: int = int(input())
students: int = int(input())
# STATE: students * [8:(String, [-inf, inf], (∅, Σ)), homeworks * [12:(Float, [-inf, inf], (∅, Σ)), 13:(Float, [0, inf], (∅, Σ))], 24:(Float, [-inf, inf], (∅, Σ)), 25:(Float, [0, inf], (∅, Σ))]
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
    print("Total homework grades:")
    print(sum)
    print("out of")
    print(best)

    best: float = float(input())
    grade: float = float(input())
    if grade < 0 or grade > best:
        raise ValueError
    print("Final test grades:")
    print(grade)
    print("out of")
    print(best)
# FINAL: ε
