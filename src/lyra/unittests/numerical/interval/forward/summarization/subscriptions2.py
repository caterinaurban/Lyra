x5: List[List[str]] = [["a", "b", "c"], ["d", "e", "f"]]
# STATE: i -> [-inf, inf]; j -> [-inf, inf]; len(x5) -> [2, 2]; x5 -> [-inf, inf]
for i in range(3):
    for j in range(2):
        if (x5[i][j] == '?' and (i < j)):
            x5[j][i]: str = ''
