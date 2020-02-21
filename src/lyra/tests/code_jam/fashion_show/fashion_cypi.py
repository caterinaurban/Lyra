def check(G: List[List[List[int]]], N: int, ii: int, jj: int) -> bool:
    for i in range(N):
        for j in range(N):
            if ((G[0][i][j] == 1) and (((i + j) == (ii + jj)) or ((i - j) == (ii - jj)))):
                return False
    return True


def add_change(G: List[List[List[int]]], C: Dict[(Tuple[(int, int)], str)], i: int, j: int) -> None:
    if (G[1][i][j] == 1):
        C[(i, j)]: str = 'o'
    else:
        C[(i, j)]: str = '+'


def do(G: List[List[List[int]]], N: int, C: Dict[(Tuple[(int, int)], str)], i: int, j: int) -> int:
    if check(G, N, i, j):
        add_change(G, C, i, j)
        G[0][i][j]: int = 1
        return 1
    return 0

_T: int = int(input())
for _t in range(1, (_T + 1)):
    line: List[str] = input().split()
    N: int = int(line[0])
    M: int = int(line[1])
    G: List[List[List[int]]] = list()
    for i in range(2):
        matrix: List[List[int]] = list()
        for j in range(N):
            row: List[int] = list()
            for k in range(N):
                row.append(0)
            matrix.append(row)
        G.append(matrix)
    score: int = 0
    for _ in range(M):
        tmp: List[str] = input().split()
        m: str = tmp[0]
        i: int = (int(tmp[1]) - 1)
        j: int = (int(tmp[2]) - 1)
        if ((m == '+') or (m == 'o')):
            G[0][i][j]: int = 1
            score += 1
        if ((m == 'x') or (m == 'o')):
            G[1][i][j]: int = 1
            score += 1
    C: Dict[(Tuple[(int, int)], str)] = dict()
    row_done: List[bool] = list()
    col_done: List[bool] = list()
    for index in range(N):
        row_done.append(False)
        col_done.append(False)

    for i in range(N):
        for j in range(N):
            if (G[1][i][j] == 1):
                row_done[i]: bool = True
                col_done[j]: bool = True
    i: int = 0
    j: int = 0
    while ((i < N) and (j < N)):
        if row_done[i]:
            i += 1
            continue
        pass
        if col_done[j]:
            j += 1
            continue
        if (G[0][i][j] == 1):
            C[(i, j)]: str = 'o'
        else:
            C[(i, j)]: str = 'x'
        row_done[i]: bool = True
        col_done[j]: bool = True
        G[1][i][j]: int = 1
        score += 1

    corners: List[Tuple[(int, int, int, int)]] = [(0, 0, 1, 1), (0, (N - 1), 1, (- 1)), ((N - 1), 0, (- 1), 1), ((N - 1), (N - 1), (- 1), (- 1))]
    for d in range(N):
        for corner in corners:
            i: int = corner[0]
            j: int = corner[1]
            di: int = corner[2]
            dj: int = corner[3]
            score += do(G, N, C, (i + (di * d)), j)
            score += do(G, N, C, i, (j + (dj * d)))
    print('Case #' + str(_t) + ':' + str(score) + ' ' + str(len(C)))
    for (i, j) in C:
        print(C[(i, j)] + ' ' + str(i + 1) + ' ' + (j + 1))
