def abs(x: int) -> int:
    if x >= 0:
        return x
    return -x

t: int = int(input())
for ti in range(1, (t + 1)):
    line: List[str] = input().split()
    m: int = int(line[0])
    n: int = int(line[1])
    cake: List[List[str]] = []
    for i in range(m):
        cake.append(['c', input()])
    for i in range(n):
        for j in range(m):
            if (cake[j][i] == '?'):
                dis: int = 100
                for k in range(m):
                    if (k == j):
                        continue
                    kj: int = abs(k - j)
                    if ((cake[k][i] != '?') and (kj < dis)):
                        dis: int = kj
                        cake[j][i]: str = cake[k][i]
    for i in range(m):
        for j in range(n):
            if (cake[i][j] == '?'):
                dis: int = 100
                for k in range(n):
                    if (k == j):
                        continue
                    kj: int = abs(k - j)
                    if ((cake[i][k] != '?') and (kj < dis)):
                        dis: int = kj
                        cake[i][j]: str = cake[i][k]
    print('Case #' + str(ti) + ':')
    for l in cake:
        print(l)
