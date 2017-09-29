def readint(): return int(raw_input())


def readarray(f): return map(f, raw_input().split())


# MAD: must be one value in line
_T = readint()
# MAD: no output if _T <= 0
for _t in range(_T):
    # MAD: must be two values in line, separated by whitespace only
    N, S = raw_input().split()
    # MAD: value must exist as int
    N = int(N)

    res = 0
    cur = 0
    for i in range(N + 1):
        if i > cur:
            res += i - cur
            cur = i
        # MAD: value must be in range: i < len(S) => N < len(S)
        cur += int(S[i])
    print('Case #%i:' % (_t + 1), res)
