
X: List[int] = [0, 5, 10]
y: int = int(input())
z: int = int(input())
if y < 2 or y > 10 or z < 3 or z > 5:
    raise ValueError
print("")
# STATE: -1·X + 10 >= 0 ∧ -1·y + 10 >= 0 ∧ -1·z + 5 >= 0 ∧ 1·z - 3 >= 0 ∧ 1·y - 2 >= 0 ∧ 1·X + 0 >= 0
if z - X[1] - y >= 0:
    # STATE: -1·X + 10 >= 0 ∧ -1·y + 1·z + 0 >= 0 ∧ -1·z + 5 >= 0 ∧ 1·z - 3 >= 0 ∧ 1·y - 2 >= 0 ∧ 1·X + 0 >= 0
    print("Ok!")
