
A: Dict[int, List[int]] = {1: [1], 2: [1, 2]}
B: List[int] = A[1]
C: List[int] = A[2]
# FINAL: A -> 1@[1, 1], 2@[1, 2], _@⊥; B -> 0@[1, 1], _@⊥; C -> 0@[1, 1], _@[2, 2]; keys(A) -> [1, 2]; len(A) -> [2, 2]; len(B) -> [0, inf]; len(C) -> [0, inf]; values(A) -> 0@[1, 1], _@[2, 2]
