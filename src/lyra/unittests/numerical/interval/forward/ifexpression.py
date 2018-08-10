
a: int = -9
b: bool = bool(input())
c: int = 9
x: int = a if b else c
# FINAL: a -> [-9, -9], b -> [0, 1], c -> [9, 9], x -> [-9, 9]
