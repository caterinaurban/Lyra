x: bool = bool(input())
# STATE: x -> U; y -> W
y: bool = bool(input())
if x:
    x: bool = x and y
    y: bool = False
if x:
    x: bool = x and y
    y: bool = False
print(y)
