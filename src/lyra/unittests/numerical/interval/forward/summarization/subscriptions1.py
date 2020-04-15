
b1: bool = bool(input())
if b1:
    y1: int = 1
else:
    y1: int = 3

x4: List[List[int]] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
# STATE: b1 -> [0, 1]; len(x4) -> [3, 3]; x4 -> [1, 9]; y1 -> [1, 3]
if x4[y1][y1-1] == 100:
    # STATE: b1 -> [0, 1]; len(x4) -> [3, 3]; x4 -> [1, 9]; y1 -> [1, 3]
    print(100)
