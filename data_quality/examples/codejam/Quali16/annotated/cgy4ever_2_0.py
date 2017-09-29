def toString(x):
    ret = ""
    for i in range(n):
        if x % 2 == 0:
            ret = '0' + ret
        else:
            ret = '1' + ret
        x /= 2
    return ret


def val(s, base):
    ret = 0
    for c in s:
        if c == '1':
            ret = ret * base + 1
        else:
            ret = ret * base
    return ret


t = input()
# MAD: must be two integers in line separated by whitespace
n, m = map(int, input().split())

v = 2 ** (n / 2) - 1
print('Case #1:')
for i in range(m):
    print(toString(v))
    print(n//2)
    t = toString(v)[n // 2:] + toString(v)[n // 2:]
    myS = t
    for b in range(2, 11):
        t += " " + str(val(toString(v), b))
    print(t)
    v -= 2
