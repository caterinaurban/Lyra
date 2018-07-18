# Source: GUC Introduction to Computer Science
import math
A: int = int(input())
B: int = int(input())
C: int = int(input())
if A < B + C: # first if
    if B < C+ A: #second if
        if C < A + B: #third if
            S = ((A + B+ C) / 2)
            Area = (math.sqrt(S * (S - A) * ( S - B) * (S - C)))
            print(" This is a triangle with the Area: ")
            print(Area)
        else: #else of 3rd if
            raise ValueError("Not a triangle")
    else: #else of 2nd if
        raise ValueError("Not a triangle")
else: #else of 1st if
    raise ValueError("Not a triangle")