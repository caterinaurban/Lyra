# RESULT: x -> N, y -> O, z -> O
x: int = int(input())
y: int = int(input())
z: int = int(input())
# RESULT: x -> N, y -> U, z -> U
if 1 < y < 3 or y < 5 and True:
    z: int = y
print(z)
