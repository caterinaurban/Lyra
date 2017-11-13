x: int = int(input())
y: int = int(input())
# RESULT: x -> U, y -> U, z -> O
z: int = 1
if y > x:
    z: int = y
else:
    z: int = y * y
print(z)
