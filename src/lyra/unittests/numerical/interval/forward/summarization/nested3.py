
D4: Dict[int, List[int]] = {1: [1, 1, 1], 2: [0, 0]}
D5: Dict[int, List[List[int]]] = {1: [[1], [1, 1]], 2: [[0], [0, 0, 0]]}
# STATE: D4 -> [0, 2]; D5 -> [0, 2]; keys(D4) -> [1, 2]; keys(D5) -> [1, 2]; len(D4) -> [2, 2]; len(D5) -> [2, 2]; values(D4) -> [0, 1]; values(D5) -> [0, 1]
D4[1][0] = 2
# STATE: D4 -> [0, 2]; D5 -> [0, 2]; keys(D4) -> [1, 2]; keys(D5) -> [1, 2]; len(D4) -> [2, 2]; len(D5) -> [2, 2]; values(D4) -> [0, 2]; values(D5) -> [0, 1]
D5[1][1][0] = 2
# STATE: D4 -> [0, 2]; D5 -> [0, 2]; keys(D4) -> [1, 2]; keys(D5) -> [1, 2]; len(D4) -> [2, 2]; len(D5) -> [2, 2]; values(D4) -> [0, 2]; values(D5) -> [0, 2]
