tests: int = int(input())
for i in range(tests):
    line: List[str] = input().strip().split()
    n: int = int(line[0])
    m: int = int(line[1])
    initmodels: List[str] = list()
    for k in range(n):
        initmodels.append(' ')
    score: int = 0
    for j in range(m):
        tmp: List[str] = input().strip().split()
        t: str = tmp[0]
        r: str = tmp[1]
        c: str = tmp[2]
        initmodels[(int(c) - 1)]: str = t
        if (t == 'o'):
            score += 2
        else:
            score += 1
    newmodels: List[str] = []
    if (('o' not in initmodels) and ('x' not in initmodels)):
        newmodels.append('o 1 1')
        inito: int = 0
        if (initmodels[0] == '+'):
            score += 1
        else:
            score += 2
    elif ('x' in initmodels):
        xc: int = initmodels.index('x')
        newmodels.append(('o 1 ' + str((xc + 1))))
        inito: int = xc
        score += 1
    else:
        oc: int = initmodels.index('o')
        inito: int = oc
    for j in range(n):
        if ((j != inito) and (initmodels[j] == ' ')):
            newmodels.append(('+ 1 ' + str((j + 1))))
            score += 1
    if (n > 2):
        for k in range(1, (n - 1)):
            if (inito == (n - 1)):
                col: int = (n - k)
            elif (k <= inito):
                col: int = k
            else:
                col: int = (k + 1)
            newmodels.append(((('x ' + str((k + 1))) + ' ') + str(col)))
            score += 1
        for k in range(2, n):
            newmodels.append(((('+ ' + str(n)) + ' ') + str(k)))
            score += 1
    if (n > 1):
        if (inito == (n - 1)):
            newmodels.append(((('x ' + str(n)) + ' ') + str(1)))
        else:
            newmodels.append(((('x ' + str(n)) + ' ') + str(n)))
        score += 1
    print(((((('Case #' + str((i + 1))) + ': ') + str(score)) + ' ') + str(len(newmodels))))
    for lin in newmodels:
        print(lin)
