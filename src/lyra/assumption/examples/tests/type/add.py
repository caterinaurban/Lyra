
x1: str = input()
x2: str = input()
# STATE: len(x) -> Integer, len(x1) -> Integer, len(x2) -> Integer, x -> String, x1 -> Integer, x2 -> Integer, y -> Float
x: str = x1 + x2
# STATE: len(x) -> Integer, len(x1) -> Integer, len(x2) -> Integer, x -> Integer, x1 -> String, x2 -> String, y -> Float
y: float = int(x)
# FINAL: len(x) -> Integer, len(x1) -> Integer, len(x2) -> Integer, x -> String, x1 -> String, x2 -> String, y -> Float
