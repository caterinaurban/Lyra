x: bool = bool(input())
# RESULT: x -> U, y -> O
y: bool = bool(input())
if x:
    x: bool = x and y
    y: bool = False
if x:
    x: bool = x and y
    y: bool = False
print(y)
