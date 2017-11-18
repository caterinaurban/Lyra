x: int = int(input())
y: int = int(input())
# STATE: x -> U, y -> U, z -> W
z: int = 1
if y > x:
    z: int = y
else:
    z: int = y * y
print(z)
