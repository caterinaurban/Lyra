_T: int = int(input())
for _t in range(_T):
    N: int = input()
    S: str = input()
    N: int = int(N)

    res: int = 0
    cur: int = 0
    for i in range(N + 1):
        if i > cur:
            res: int = res + i - cur
            cur: int = i
        cur: int = cur + int(S[i])
    print('Case #:')
    print(_t + 1)
    print(res)