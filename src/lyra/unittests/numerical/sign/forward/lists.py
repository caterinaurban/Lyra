# INITIAL: a -> ⊤; l1 -> ⊤; l2 -> ⊤; len(l1) -> ⊤; len(l2) -> ⊤
l1: List[int] = [-1, 0]
# STATE: a -> ⊤; l1 -> ≤0; l2 -> ⊤; len(l1) -> ⊤; len(l2) -> ⊤
l2: List[int] = [0, 0]
# STATE: a -> ⊤; l1 -> ≤0; l2 -> =0; len(l1) -> ⊤; len(l2) -> ⊤
a: int = l1[0]
# STATE: a -> ≤0; l1 -> ≤0; l2 -> =0; len(l1) -> ⊤; len(l2) -> ⊤
l2[0]: int = 1
# STATE: a -> ≤0; l1 -> ≤0; l2 -> ≥0; len(l1) -> ⊤; len(l2) -> ⊤
l2[0]: int = a
# FINAL: a -> ≤0; l1 -> ≤0; l2 -> ⊤; len(l1) -> ⊤; len(l2) -> ⊤
