
# INITIAL: b -> [-inf, inf]; q -> [-inf, inf]; z -> [-inf, inf]
b: bool = bool(input())
# STATE: b -> [0, 1]; q -> [-inf, inf]; z -> [-inf, inf]
q: bool = bool(input())
# STATE: b -> [0, 1]; q -> [0, 1]; z -> [-inf, inf]
z: int = 1
# STATE: b -> [0, 1]; q -> [0, 1]; z -> [1, 1]
if b and q:
    # STATE: b -> [1, 1]; q -> [1, 1]; z -> [1, 1]
    z = 1
    # STATE: b -> [1, 1]; q -> [1, 1]; z -> [1, 1]
else:
    # STATE: b -> [0, 1]; q -> [0, 1]; z -> [1, 1]
    z = 0
    # STATE: b -> [0, 1]; q -> [0, 1]; z -> [0, 0]
# STATE: b -> [0, 1]; q -> [0, 1]; z -> [0, 1]
print(z)
# FINAL: b -> [0, 1]; q -> [0, 1]; z -> [0, 1]
