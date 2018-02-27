# Analysis finds: (int, _T x [int, str])

_T: int = int(input())  # inlined a method call
for _t in range(_T):
    N_str: str = input()  # instead of N, S = input().split(), renamed N to N_str
    S: str = input()
    N: int = int(N_str)

    res: float = 0
    cur: int = 0
    for i in range(N + 1):
        if i > cur:
            res: float = res + (i - cur)  # rewritten +=
            cur: float = i
        cur: float = cur + int(S[i])  # rewritten +=
    print('Case #')  # print without multiple arguments and modulo
    print(_t + 1)
    print(':')
    print(res)
