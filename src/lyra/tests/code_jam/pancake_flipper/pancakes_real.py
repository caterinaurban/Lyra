def all_true(a: List[bool]) -> bool:
    for i in range(len(a)):
        if a[i] == False:
            return False
    return True

def gao(s: str, k: int) -> int:
    a: List[bool] = list()
    c: str = ''
    for c in s:
        if c == '+':
            a.append(True)
        else:
            a.append(False)
    n: int = len(s)
    ans: int = 0
    for i in range(((n - k) + 1)):
        if a[i] == False:
            for j in range(k):
                a[(i + j)]: bool = (not a[(i + j)])
            ans += 1
    if all_true(a):
        return ans
    return (- 1)


for no_t in range(1, (int(input()) + 1)):
    line: List[str] = input().split()
    s: str = line[0]
    k: str = line[1]
    result: int = gao(s, int(k))
    if (result == (- 1)):
        print('Case #' + str(no_t) + ': ' + 'IMPOSSIBLE')
    else:
        print('Case #' + str(no_t) + ': ' + str(result))
