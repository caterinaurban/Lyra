
x1: List[int] = [0, 0, 0]
# STATE: T -> [-inf, inf]; b1 -> [-inf, inf]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [0, inf]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 0], 2@[0, 0], _@⊥; x2 -> _@[-inf, inf]; x3 -> _@[-inf, inf]; y1 -> [-inf, inf]
b1: bool = bool(input())
if b1:
    y1: int = 1
else:
    y1: int = 3

# STATE: T -> [-inf, inf]; b1 -> [0, 1]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [0, inf]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 0], 2@[0, 0], _@⊥; x2 -> _@[-inf, inf]; x3 -> _@[-inf, inf]; y1 -> [1, 3]
x1[y1] = 9
# STATE: T -> [-inf, inf]; b1 -> [0, 1]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [0, inf]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 9], 2@[0, 9], _@[9, 9]; x2 -> _@[-inf, inf]; x3 -> _@[-inf, inf]; y1 -> [1, 3]

x2: List[int] = list()
# STATE: T -> [-inf, inf]; b1 -> [0, 1]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [0, 0]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 9], 2@[0, 9], _@[9, 9]; x2 -> _@⊥; x3 -> _@[-inf, inf]; y1 -> [1, 3]
T: int = 5
# STATE: T -> [5, 5]; b1 -> [0, 1]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [0, 0]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 9], 2@[0, 9], _@[9, 9]; x2 -> _@⊥; x3 -> _@[-inf, inf]; y1 -> [1, 3]
for i in range(T):
    # STATE: T -> [5, 5]; b1 -> [0, 1]; i -> [0, 4]; len(x1) -> [3, 3]; len(x2) -> [0, inf]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 9], 2@[0, 9], _@[9, 9]; x2 -> _@[0, 4]; x3 -> _@[-inf, inf]; y1 -> [1, 3]
    x2.append(i)

# STATE: T -> [5, 5]; b1 -> [0, 1]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [0, inf]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 9], 2@[0, 9], _@[9, 9]; x2 -> _@[0, 4]; x3 -> _@[-inf, inf]; y1 -> [1, 3]
x2[T] = x2[T] + 1
# STATE: T -> [5, 5]; b1 -> [0, 1]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [6, inf]; len(x3) -> [0, inf]; x1 -> 0@[0, 0], 1@[0, 9], 2@[0, 9], _@[9, 9]; x2 -> 5@[1, 5], _@[0, 4]; x3 -> _@[-inf, inf]; y1 -> [1, 3]

x3: List[int] = list()
# STATE: T -> [5, 5]; b1 -> [0, 1]; i -> [-inf, inf]; len(x1) -> [3, 3]; len(x2) -> [6, inf]; len(x3) -> [0, 0]; x1 -> 0@[0, 0], 1@[0, 9], 2@[0, 9], _@[9, 9]; x2 -> 5@[1, 5], _@[0, 4]; x3 -> _@⊥; y1 -> [1, 3]
x3[1] = 0
# FINAL: T -> ⊥; b1 -> ⊥; i -> ⊥; len(x1) -> ⊥; len(x2) -> ⊥; len(x3) -> ⊥; x1 -> ⊥; x2 -> ⊥; x3 -> ⊥; y1 -> ⊥
