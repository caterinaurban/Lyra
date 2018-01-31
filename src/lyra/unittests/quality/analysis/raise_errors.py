# INITIAL [2:(Float, [5, 40]), 3:(Float, [10, 20])]
a: float = float(input())
b: float = float(input())
if b < 10:
    raise ValueError
if b > 20:
    raise ValueError("Error!")
if a < 5:
    raise Exception
if a > 40:
    raise Exception("Error!")
