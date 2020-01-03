def flips(s: str, k: int) -> int:
    if (len(s) < k):
        pancake: str = ''
        for pancake in s:
            if (pancake == '-'):
                return (- 1)
        return 0
    elif (s[0] == '-'):
        a: str = ''
        for i in range(k):
            if (s[i] == '-'):
                a += '+'
            else:
                a += '-'
        new: str = (a + s[k:])
        subresult: int = flips(new, k)
        if (subresult == (- 1)):
            return (- 1)
        else:
            return (subresult + 1)
    else:
        return flips(s[1:], k)

t: int = int(input())
for i in range(1, (t + 1)):
    line: List[str] = input().split(' ')
    result: int = flips(line[0], int(line[1]))
    if (result != (- 1)):
        print('Case #' + str(i) + ': ' + str(result))
    else:
        print('Case #' + str(i) + ': ' + 'IMPOSSIBLE')
