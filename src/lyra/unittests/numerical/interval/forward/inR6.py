
x: int = 2
# STATE: x -> [2, 2]
if x in range(int(input())):
    # STATE: x -> [2, 2]
    print(x)
else:
    raise ValueError
# FINAL: x -> [2, 2]
