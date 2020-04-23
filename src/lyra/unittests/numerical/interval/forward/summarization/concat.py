
L1: List[int] = [1, 2, 3]
L2: List[int] = [4, 5, 6]
L3: List[int] = L1 + L2
# STATE: L1 -> [1, 3]; L2 -> [4, 6]; L3 -> [1, 6]; len(L1) -> [3, 3]; len(L2) -> [3, 3]; len(L3) -> [6, 6]
L1: List[int] = []
L2: List[int] = [4, 5, 6]
L3: List[int] = L1 + L2
# STATE: L1 -> ⊥; L2 -> [4, 6]; L3 -> [4, 6]; len(L1) -> [0, 0]; len(L2) -> [3, 3]; len(L3) -> [3, 3]
L1: List[int] = [1, 2, 3]
L2: List[int] = []
L3: List[int] = L1 + L2
# STATE: L1 -> [1, 3]; L2 -> ⊥; L3 -> [1, 3]; len(L1) -> [3, 3]; len(L2) -> [0, 0]; len(L3) -> [3, 3]
L1: List[int] = [1]
L2: List[int] = [4, 5, 6]
L3: List[int] = L1 + L2
# STATE: L1 -> [1, 1]; L2 -> [4, 6]; L3 -> [1, 6]; len(L1) -> [1, 1]; len(L2) -> [3, 3]; len(L3) -> [4, 4]
L1: List[int] = [1, 2]
L2: List[int] = [4]
L3: List[int] = L1 + L2
# FINAL: L1 -> [1, 2]; L2 -> [4, 4]; L3 -> [1, 4]; len(L1) -> [2, 2]; len(L2) -> [1, 1]; len(L3) -> [3, 3]
