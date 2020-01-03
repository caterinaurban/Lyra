def score(l: List[List[str]], n: int) -> int:
    s: int = 0
    for i in range(n):
        for j in range(n):
            if (l[i][j] == 'o'):
                s += 2
            if ((l[i][j] == '+') or (l[i][j] == 'x')):
                s += 1
    return s

t: int = int(input())
for t_index in range(t):
    line: List[str] = input().split()
    n: int = int(line[0])
    m: int = int(line[1])
    l: List[List[str]] = []
    l_beg: List[List[str]] = []
    for _ in range(n):
        l.append([])
        l_beg.append([])
        for _ in range(n):
            l[(- 1)].append('')
            l_beg[(- 1)].append('')
    for _ in range(m):
        tmp: List[str] = input().split()
        c: str = tmp[0]
        i: int = (int(tmp[1]) - 1)
        j: int = (int(tmp[2]) - 1)
        l[i][j]: str = c
        l_beg[i][j]: str = c
    l0: List[str] = l[0]
    index: int = (- 1)
    if (l0.count('o') == 0):
        if (l0.count('x') == 1):
            for i in range(n):
                if (l0[i] == 'x'):
                    l0[i]: str = 'o'
                    index: int = i
                if (l0[i] == ''):
                    l0[i]: str = '+'
        else:
            p: bool = False
            for i in range(n):
                if (l0[i] == ''):
                    if (not p):
                        l0[i]: str = 'o'
                        index: int = i
                        p: bool = True
                    else:
                        l0[i]: str = '+'
            if (not p):
                l0[0]: str = 'o'
                index: int = 0
    else:
        for i in range(n):
            if (l0[i] == ''):
                l0[i]: str = '+'
            if (l0[i] == 'o'):
                index: int = i
    i: int = 0
    if (index != (n - 1)):
        for j in range(1, n):
            if (i == index):
                i += 1
            l[j][i]: str = 'x'
            i += 1
    else:
        for j in range(1, n):
            l[j][((n - 1) - j)]: str = 'x'
            i += 1
    ln: List[str] = l[(- 1)]
    for i in range(1, (n - 1)):
        ln[i]: str = '+'
    s: int = score(l, n)
    changes: List[Tuple[(str, int, int)]] = []
    for i in range(n):
        for j in range(n):
            if (l[i][j] != l_beg[i][j]):
                changes.append((l[i][j], (i + 1), (j + 1)))
    print(((((('Case #' + str((t_index + 1))) + ': ') + str(s)) + ' ') + str(len(changes))))
    for r in changes:
        print(str(r[0]) + ' ' + str(r[1]) + ' ' + str(r[2]))
