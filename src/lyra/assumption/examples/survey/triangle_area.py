# Source: GUC Introduction to Computer Science
A: int = int(input())
B: int = int(input())
C: int = int(input())
if A < B + C:  # first if
    if B < C + A:  # second if
        if C < A + B:  # third if
            print(" This is a triangle with the Area: ")
        else:  # else of 3rd if
            raise ValueError("Not a triangle")
    else:  # else of 2nd if
        raise ValueError("Not a triangle")
else:  # else of 1st if
    raise ValueError("Not a triangle")
