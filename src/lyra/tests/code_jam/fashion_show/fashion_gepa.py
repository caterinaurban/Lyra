def delta(N: int, x: List[List[str]], y: List[List[str]]) -> str:
    total: int = 0
    res: List[str] = list()
    for r in range(N):
        for c in range(N):
            if (x[r][c] != y[r][c]):
                rr: int = r + 1
                cc: int = c + 1
                res.append(y[r][c] + ' ' + str(rr) + ' ' + str(cc))
            if (y[r][c] in ['+', 'x']):
                total += 1
            elif (y[r][c] == 'o'):
                total += 2
    diff: int = len(res) - 1
    res[0]: str = str(total) + ' ' + str(diff)
    res_str: str = ''
    for index in range(len(res)):
        res_str += res[index] + '\n'
    return res_str

def compute(N: int, x: List[List[str]]) -> str:
    y: List[List[str]] = list()
    for index in range(N):
        y_row: List[str] = list()
        for j in range(N):
            y_row.append('.')
        y.append(y_row)
    if (N == 1):
        y[0][0]: str = 'o'
        return delta(N, x, y)
    for r in range(N):
        for c in range(N):
            y[r][c]: str = x[r][c]
    cx: int = 0
    for c in range(N):
        if (x[0][c] in ['x', 'o']):
            cx: int = c
            break
    for c in range(N):
        y[0][c]: str = '+'
    y[0][cx]: str = 'o'
    for c in range(1, (N - 1)):
        y[(N - 1)][c]: str = '+'
    if (cx == (N - 1)):
        y[(N - 1)][0]: str = 'x'
        cx: int = 0
    else:
        y[(N - 1)][(N - 1)]: str = 'x'
    for r in range(1, (N - 1)):
        if (r <= cx):
            y[r][(r - 1)]: str = 'x'
        else:
            y[r][r]: str = 'x'
    return delta(N, x, y)

def parse() -> Tuple[(int, List[List[str]])]:
    line: List[str] = input().strip().split()
    N: int = int(line[0])
    M: int = int(line[1])
    x: List[List[str]] = list()
    for index in range(N):
        x_row: List[str] = list()
        for j in range(N):
            x_row.append('.')
        x.append(x_row)
    for i in range(M):
        arc: List[str] = input().strip().split()
        a: str = arc[0]
        r: int = (int(arc[1]) - 1)
        c: int = (int(arc[2]) - 1)
        x[r][c]: str = a
    return (N, x)

T: int = int(input().strip())
part: int = int(input())
count: int = int(input())
for i in range(T):
    parse_result: Tuple[(int, List[List[str]])] = parse()
    N: int = parse_result[0]
    data: List[List[str]] = parse_result[1]
    if (((i * count) >= (part * T)) and ((i * count) < ((part + 1) * T))):
        result: str = compute(N, data)
        print('Case #' + str(i + 1) + ':' + result)
