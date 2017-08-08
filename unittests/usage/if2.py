# RESULT: x -> ⟂, y -> ⫱, z -> ⫱
x = y = z = int(input())
# RESULT: x -> ⟂, y -> ⚫, z -> ⚫
if 1 < y < 3 or y < 5 and True:
    z = y
print(z)
