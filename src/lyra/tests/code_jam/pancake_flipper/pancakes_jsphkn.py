

def flips(s: str, k: int) -> None:
    if (len(s) < k):
        for pancake in s:
            if (pancake == '-'):
                return 'IMPOSSIBLE'
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
        if (subresult == 'IMPOSSIBLE'):
            return 'IMPOSSIBLE'
        else:
            return (subresult + 1)
    else:
        subresult: None = flips(s[1:], k)
        if (subresult == 'IMPOSSIBLE'):
            return 'IMPOSSIBLE'
        else:
            return subresult
t: int = int(input())
for i in range(1, (t + 1)):
    (s, k) = input().split(' ')
    print('Case #{}: {}'.format(i, flips(s, int(k))))
