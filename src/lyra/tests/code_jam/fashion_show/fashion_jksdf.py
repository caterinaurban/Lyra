def printout(n: int, v: str) -> None:
    print(((('Case #' + str(n)) + ': ') + v))

def call(ii: int) -> None:
    line: List[str] = input().split()
    n: int = int(line[0])
    m: int = int(line[1])
    row: List[str] = list()
    for i in range(n):
        row.append(' ')
    nonplus: int = (- 1)
    for i in range(m):
        tmp: List[str] = input().split()
        v: str = tmp[0]
        r: str = tmp[1]
        c: str = tmp[2]
        row[(int(c) - 1)]: str = v
        if (v != '+'):
            nonplus: int = (int(c) - 1)
    res: List[Tuple[(str, int, int)]] = []
    if (nonplus == (- 1)):
        nonplus: int = 0
        row[0]: str = 'o'
        res.append(('o', 0, 0))
    for i in range(len(row)):
        v: str = row[i]
        if (v == ' '):
            res.append(('+', 0, i))
        elif (v == 'x'):
            res.append(('o', 0, i))
            nonplus: int = i
    for i in range(0, nonplus):
        res.append(('x', (i + 1), i))
    for i in range((nonplus + 1), n):
        res.append(('x', i, i))
    for i in range(1, (n - 1)):
        res.append(('+', (n - 1), i))
    number: int = 2
    if n != 1:
        number = (3 * n) - 2
    printout(ii, str(number) + ' ' + str(len(res)))
    for ituple in res:
        print(((str(ituple[0]) + str((int(ituple[1]) + 1))) + str((int(ituple[2]) + 1))))
t: int = int(input())
for ii in range(t):
    call((ii + 1))
