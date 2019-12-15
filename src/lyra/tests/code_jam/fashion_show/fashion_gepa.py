def delta(N: int, x: List[List[str]], y: List[List[str]]) -> str:
    total: int = 0
    res: List[str] = [None]
    for r in range(N):
        for c in range(N):
            if (x[r][c] != y[r][c]):
                res.append(('%s %d %d' % (y[r][c], (r + 1), (c + 1))))
            if (y[r][c] in ['+', 'x']):
                total += 1
            elif (y[r][c] == 'o'):
                total += 2
    res[0]: str = ('%d %d' % (total, (len(res) - 1)))
    return '\n'.join(res)

def compute(N: int, x: List[List[str]]) -> str:
    y: List[List[str]] = [(['.'] * N) for i in range(N)]
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
    line: List[str] = sys.stdin.readline().strip().split()
    N: int = int(line[0])
    M: int = int(line[1])
    x: List[List[str]] = [(['.'] * N) for i in range(N)]
    for i in range(M):
        arc: List[str] = sys.stdin.readline().strip().split()
        a: str = arc[0]
        r: int = (int(arc[1]) - 1)
        c: int = (int(arc[2]) - 1)
        x[r][c]: str = a
    return (N, x)
if (__name__ == '__main__'):
    sys.setrecursionlimit(100000)
    T: int = int(sys.stdin.readline().strip())
    count: int = 1
    part: int = 0
    if (len(sys.argv) == 3):
        part: int = int(sys.argv[1])
        count: int = int(sys.argv[2])
    for i in range(T):
        (N, data) = parse()
        if (((i * count) >= (part * T)) and ((i * count) < ((part + 1) * T))):
            result: str = compute(N, data)
            print(('Case #%d: %s' % ((i + 1), result)))
