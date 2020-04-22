
X: List[int] = [0, 5, 10]
y: int = int(input())
z: int = int(input())
if y < 2 or y > 10 or z < 3 or z > 5:
    raise ValueError
print("")
# STATE: X -> 0@[0, 0], 1@[5, 5], 2@[10, 10], _@⊥; len(X) -> [3, 3]; y -> [2, 10]; z -> [3, 5]
if X[1] - y - z >= 0:
    # STATE: X -> 0@[0, 0], 1@[5, 5], 2@[10, 10], _@⊥; len(X) -> [3, 3]; y -> [2, 2]; z -> [3, 3]
    print("OK!")
