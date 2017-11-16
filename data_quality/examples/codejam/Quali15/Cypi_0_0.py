def readint(): return int(input())


def readarray(f): return map(f, input().split())


# MAD: must be one value in line
_T = readint()
# MAD: no output if _T <= 0
# MAD: number of lines after first line >= T
for _t in range(_T):
    # MAD: must be two values in line, separated by whitespace only
    # MAD: value must be in range N + 1 < len(S)
    # MAD: values in S must be ints
    N, S = input().split()
    # MAD: value must exist as int
    N = int(N)

    res = 0
    cur = 0
    # MAD: value must be in range: N + 1 < len(S)
    for i in range(N + 1):
        if i > cur:
            res += i - cur
            cur = i
        # MAD: value must be in range: i < len(S)
        # MAD: elements must be digits: S
        cur += int(S[i])
    print('Case #%i:' % (_t + 1), res)
