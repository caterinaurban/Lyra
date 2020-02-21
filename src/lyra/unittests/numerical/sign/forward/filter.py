
x: int = int(input())
y: int = int(input())
z: int = int(input())
if x < 0 or x > 10 or y < 2 or y > 10 or z < 3 or z > 5:
    raise ValueError
print("")
# STATE: x -> ≥0; y -> >0; z -> >0
if z - x - y >= 0:
    # STATE: x -> ≥0; y -> >0; z -> >0
    print("Ok!")
