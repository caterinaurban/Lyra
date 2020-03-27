def copy(original: List[List[str]]) -> List[List[str]]:
    new_list: List[List[str]] = list()
    for line in original:
        new_list.append(line[:])
    print(new_list)
    return new_list


R: int = int(input())
matrix: List[List[str]] = []
for row in range(R):
    matrix.append(list(input()))
result: List[List[str]] = copy(matrix)
