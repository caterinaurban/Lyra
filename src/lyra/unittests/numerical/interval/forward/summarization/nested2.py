
D1: Dict[int, int] = {1: 1}
D2: Dict[int, List[int]] = {1: [1, 1, 1]}
D3: Dict[int, Dict[int, int]] = {1: {1: 1}}
# STATE: D1 -> [1, 1]; D2 -> [1, 1]; D3 -> [1, 1]; keys(D1) -> [1, 1]; keys(D2) -> [1, 1]; keys(D3) -> [1, 1]; len(D1) -> [1, 1]; len(D2) -> [1, 1]; len(D3) -> [1, 1]; values(D1) -> [1, 1]; values(D2) -> [1, 1]; values(D3) -> [1, 1]
D1[2] = 1
# STATE: D1 -> [1, 2]; D2 -> [1, 1]; D3 -> [1, 1]; keys(D1) -> [1, 2]; keys(D2) -> [1, 1]; keys(D3) -> [1, 1]; len(D1) -> [2, 2]; len(D2) -> [1, 1]; len(D3) -> [1, 1]; values(D1) -> [1, 1]; values(D2) -> [1, 1]; values(D3) -> [1, 1]
D1[1] = 2
# STATE: D1 -> [1, 2]; D2 -> [1, 1]; D3 -> [1, 1]; keys(D1) -> [1, 2]; keys(D2) -> [1, 1]; keys(D3) -> [1, 1]; len(D1) -> [2, 3]; len(D2) -> [1, 1]; len(D3) -> [1, 1]; values(D1) -> [1, 2]; values(D2) -> [1, 1]; values(D3) -> [1, 1]
D2[1][0] = 2
# STATE: D1 -> [1, 2]; D2 -> [1, 2]; D3 -> [1, 1]; keys(D1) -> [1, 2]; keys(D2) -> [1, 1]; keys(D3) -> [1, 1]; len(D1) -> [2, 3]; len(D2) -> [1, 1]; len(D3) -> [1, 1]; values(D1) -> [1, 2]; values(D2) -> [1, 2]; values(D3) -> [1, 1]
D3[1][0] = 2
# FINAL: D1 -> [1, 2]; D2 -> [1, 2]; D3 -> [0, 2]; keys(D1) -> [1, 2]; keys(D2) -> [1, 1]; keys(D3) -> [1, 1]; len(D1) -> [2, 3]; len(D2) -> [1, 1]; len(D3) -> [1, 1]; values(D1) -> [1, 2]; values(D2) -> [1, 2]; values(D3) -> [0, 2]
