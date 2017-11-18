x: int = int(input())
y: int = int(input())
# STATE: x -> U, y -> N, b -> N, a -> W
if 3 > x:  # x decision
    # inside nested if only b is modified!
    if 2 > y:  # y decision
        b: int = 10
    else:
        b: int = 20
    a: int = 10
else:
    # inside nested if only b is modified!
    if 2 > y:  # y decision
        b: int = 10
    else:
        b: int = 20
    a: int = 20
print(a)
