from random import *

def fromBase(s, b):
    n = 0
    for c in s:
        n = b * n + ord(c) - ord('0')
    return n

print('Case #1:')
t = input()
# MAD: input has to be two integers separated by whitespace
n, q = map(int, input().split())
M = 1000
a = set()
while len(a) < q:
    s = '1' + ''.join(['01'[randrange(2)] for i in range(n - 2)]) + '1'
    if s in a:
        continue
    l = []
    for b in range(2, 11):
        N = fromBase(s, b)
        t = -1
        for j in range(2, M + 1):
            if j >= N:
                break
            if N % j == 0:
                t = j
                break
        l.append(t)
    if -1 in l:
        continue
    print(s, ' '.join(map(str, l)))
    a.add(s)
