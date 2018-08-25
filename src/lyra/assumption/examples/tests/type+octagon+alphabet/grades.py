
# 3:(String, T, (∅, Σ)), 4:(Integer, T, (∅, Σ)), 5:(Integer, T, (∅, Σ)), 5.1 * [8:(String, T, (∅, {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})), 4.1 * [12:(Float, OCT(12.1 >= 0), (∅, Σ)), 13:(Float, OCT(13.1 >= 0,13.1 + 12.1 >= 0,12.1 >= 0,13.1 >= 12.1), (∅, Σ))], 27:(Float, OCT(27.1 >= 0), (∅, Σ)), 28:(Float, OCT(28.1 >= 0,28.1 + 27.1 >= 0,27.1 >= 0,28.1 >= 27.1), (∅, Σ))]
subject: str = input()
homeworks: int = int(input())
students: int = int(input())
# STATE: students * [8:(String, [-inf, inf], (∅, Σ)), homeworks * [12:(Float, [-inf, inf], (∅, Σ)), 13:(Float, [0, inf], (∅, Σ))], 24:(Float, [-inf, inf], (∅, Σ)), 25:(Float, [0, inf], (∅, Σ))]
for i in range(students):
    id: str = input()
    sum: float = 0
    max: float = 0
    for j in range(homeworks):
        grade: float = float(input())
        best: float = float(input())
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

    grade: float = float(input())
    best: float = float(input())
    if grade < 0 or grade > best:
        raise ValueError
    print("Final test grades:")
    print(grade)
    print("out of")
    print(best)
# FINAL: ε
# TOTAL ASSUMPTIONS:
# SOUND ASSUMPTIONS:
# IMPRECISIONS:
# LINE        DOMAIN      COMMENT