# INITIAL: x -> N, y -> W, z -> W
x: int = int(input())
y: int = int(input())
z: int = int(input())
# STATE: x -> N, y -> U, z -> U
if 1 < y < 3 or y < 5 and True:
    z: int = y
print(z)
