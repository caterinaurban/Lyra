T: int = int(input())
for t in range(1, (T + 1)):
    line: List[str] = input().split()
    S: str = line[0]
    K: int = int(line[1])
    a: List[int] = list()
    for index in range(len(S)):
        a.append(0)
    for i in range(len(S)):
        if (S[i] == '-'):
            a[i] += 1
    cnt: int = 0
    for i in range(((len(S) - K) + 1)):
        if ((a[i] % 2) == 1):
            cnt += 1
            for j in range(K):
                a[(i + j)] += 1
    is_valid: bool = True
    for i in range(len(S)):
        if ((a[i] % 2) == 1):
            is_valid: bool = False
            break
    if is_valid:
        print(((('Case #' + str(t)) + ': ') + str(cnt)))
    else:
        print((('Case #' + str(t)) + ': IMPOSSIBLE'))
