
x: int = int(input())
y: int = int(input())
z: int = int(input())
if x < 0 or x > 10 or y < 2 or y > 10 or z < 3 or z > 5:
    raise ValueError
print("")
# STATE: -1·x + 10 >= 0 ∧ -1·y + 10 >= 0 ∧ -1·z + 5 >= 0 ∧ 1·z - 3 >= 0 ∧ 1·y - 2 >= 0 ∧ 1·x + 0 >= 0
if z - x - y >= 0:
    # STATE: -1·x - 1·y + 1·z + 0 >= 0 ∧ -1·z + 5 >= 0 ∧ 1·z - 3 >= 0 ∧ 1·y - 2 >= 0 ∧ 1·x + 0 >= 0
    print("Ok!")
