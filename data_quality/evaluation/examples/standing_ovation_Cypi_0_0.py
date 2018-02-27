_T: int = int(input())
for _t in range(_T):
    N_str: str = input()
    S: str = input()
    N: int = int(N_str)

    res: float = 0
    cur: int = 0
    for i in range(N + 1):
        if i > cur:
            res: float = res + (i - cur)
            cur: float = i
        cur: int = cur + int(S[i])
    print('Case #')
    print(_t + 1)
    print(':')
    print(res)
