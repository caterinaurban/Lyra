# INITIAL: l1 -> ⊤, l2 -> ⊤, a -> ⊤
l1: List[int] = [-1, 0]
# STATE: l1 -> ≤0, l2 -> ⊤, a -> ⊤
l2: List[int] = [0, 0]
# STATE: l1 -> ≤0, l2 -> =0, a -> ⊤
a: int = l1[0]
# STATE: l1 -> ≤0, l2 -> =0, a -> ≤0
l2[0]: int = 1
# STATE: l1 -> ≤0, l2 -> ≥0, a -> ≤0
l2[0]: int = a
# FINAL: l1 -> ≤0, l2 -> ⊤, a -> ≤0
