
x1: str = input()
x2: str = input()
# STATE: x1 -> Integer, x2 -> Integer, x -> String, y -> Float
x: str = x1 + x2
# STATE: x1 -> String, x2 -> String, x -> Integer, y -> Float
y: float = int(x)
# FINAL: x1 -> String, x2 -> String, x -> String, y -> Float
