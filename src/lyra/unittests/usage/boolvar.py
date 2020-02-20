
b: bool = bool(input())
q: bool = bool(input())
# STATE: b -> U; q -> U; z -> W
z: int = 1 if b and q else 0
print(z)
