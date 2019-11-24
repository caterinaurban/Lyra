
from typing import List
T: int = int(input())
for iT in list(range(0, T)):
    lim: List[str] = input().split()
    N: int = int(lim[0])
    M: int = int(lim[1])
    a: List[List[None]] = []
    for i in list(range(0, N)):
        a.append(list(input()))
    cnt: int = 0
    for i in list(range(0, N)):
        for j in list(range(0, M)):
            if (a[i][j] == '?'):
                cnt: int = (cnt + 1)
    while (cnt > 0):
        for i in list(range(0, N)):
            for j in list(range(0, M)):
                if (a[i][j] != '?'):
                    orig: None = a[i][j]
                    if ((j + 1) < M):
                        if (a[i][(j + 1)] == '?'):
                            l: int = i
                            r: int = i
                            while ((l >= 0) and (a[l][j] == orig)):
                                l: int = (l - 1)
                            while ((r < N) and (a[r][j] == orig)):
                                r: int = (r + 1)
                            flag: int = True
                            for z in list(range((l + 1), r)):
                                if (a[z][(j + 1)] != '?'):
                                    flag: int = False
                            if flag:
                                for z in list(range((l + 1), r)):
                                    a[z][(j + 1)]: None = orig
                                    cnt: int = (cnt - 1)
                    if ((j - 1) >= 0):
                        if (a[i][(j - 1)] == '?'):
                            l: int = i
                            r: int = i
                            while ((l >= 0) and (a[l][j] == orig)):
                                l: int = (l - 1)
                            while ((r < N) and (a[r][j] == orig)):
                                r: int = (r + 1)
                            flag: int = True
                            for z in list(range((l + 1), r)):
                                if (a[z][(j - 1)] != '?'):
                                    flag: int = False
                            if flag:
                                for z in list(range((l + 1), r)):
                                    a[z][(j - 1)]: None = orig
                                    cnt: int = (cnt - 1)
                    if ((i + 1) < N):
                        if (a[(i + 1)][j] == '?'):
                            l: int = j
                            r: int = j
                            while ((l >= 0) and (a[i][l] == orig)):
                                l: int = (l - 1)
                            while ((r < M) and (a[i][r] == orig)):
                                r: int = (r + 1)
                            flag: int = True
                            for z in list(range((l + 1), r)):
                                if (a[(i + 1)][z] != '?'):
                                    flag: int = False
                            if flag:
                                for z in list(range((l + 1), r)):
                                    a[(i + 1)][z]: None = orig
                                    cnt: int = (cnt - 1)
                    if ((i - 1) >= 0):
                        if (a[(i - 1)][j] == '?'):
                            l: int = j
                            r: int = j
                            while ((l >= 0) and (a[i][l] == orig)):
                                l: int = (l - 1)
                            while ((r < M) and (a[i][r] == orig)):
                                r: int = (r + 1)
                            flag: int = True
                            for z in list(range((l + 1), r)):
                                if (a[(i - 1)][z] != '?'):
                                    flag: int = False
                            if flag:
                                for z in list(range((l + 1), r)):
                                    a[(i - 1)][z]: None = orig
                                    cnt: int = (cnt - 1)
    print((('Case #' + str((iT + 1))) + ':'))
    for i in list(range(0, N)):
        for j in list(range(0, M)):
            print(a[i][j], end='')
        print()
