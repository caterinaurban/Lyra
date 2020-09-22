
x1: str = input()
x2: str = input()
# STATE: len(x) -> [0, inf]; len(x1) -> [0, inf]; len(x2) -> [0, inf]; x -> String; x1 -> Integer; x2 -> Integer; y -> Float
x: str = x1 + x2
# STATE: len(x) -> [0, inf]; len(x1) -> [0, inf]; len(x2) -> [0, inf]; x -> Integer; x1 -> String; x2 -> String; y -> Float
y: float = int(x)
# FINAL: len(x) -> [0, inf]; len(x1) -> [0, inf]; len(x2) -> [0, inf]; x -> String; x1 -> String; x2 -> String; y -> Float
