

_T = int(input())
for _t in range(_T):
    N, S = input().split()
    N = int(N)

    res = 0
    cur = 0
    for i in range(N + 1):
        if i > cur:
            res += i - cur
            cur = i
        cur += int(S[i])
    print('Case #%i:' % (_t + 1), res)
