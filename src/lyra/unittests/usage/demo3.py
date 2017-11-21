x: int = int(input())
y: int = int(input())

# STATE: x -> U, y -> N, a -> W, b -> N

if 3 > x:  # x decision
    # inside nested if only b is modified!
    if 2 > y:  # y decision
        b: int = 10
    else:
        b: int = 20
    a: int = 10
else:
    a: int = 20
print(a)

