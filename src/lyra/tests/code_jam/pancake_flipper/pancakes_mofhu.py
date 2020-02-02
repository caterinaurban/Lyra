n: int = int(input())
for case in range(1, (n + 1)):
    line: List[str] = input().split()
    tmps: str = line[0]
    tmpk: str = line[1]
    s: List[str] = list(tmps)
    k: int = int(tmpk)
    n: int = 0
    for i in range(0, len(s)):
        if (s[i] == '-'):
            if (i > (len(s) - k)):
                print('Case #' + str(case) + ': ' + 'IMPOSSIBLE')
                break
            else:
                n += 1
                for i in range((i + 1), (i + k)):
                    if (s[i] is '-'):
                        s[i]: str = '+'
                    else:
                        s[i]: str = '-'
        else:
            pass
    else:
        print('Case #' + str(case) + ': ' + str(n))
