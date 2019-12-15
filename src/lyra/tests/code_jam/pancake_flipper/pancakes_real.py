sys.setrecursionlimit(10000)

def gao(s: str, k: int) -> int:
    a: List[bool] = [(c == '+') for c in s]
    n: int = len(s)
    ans: int = 0
    for i in range(((n - k) + 1)):
        if (not a[i]):
            for j in range(k):
                a[(i + j)]: bool = (not a[(i + j)])
            ans += 1
    if all(a):
        return ans
    return (- 1)
for no_t in range(1, (int(input()) + 1)):
    line: List[str] = input().split()
    s: str = line[0]
    k: str = line[1]
    result: int = gao(s, int(k))
    if (result == (- 1)):
        print(('Case #%d: %s' % (no_t, 'IMPOSSIBLE')))
    else:
        print(('Case #%d: %s' % (no_t, result)))
