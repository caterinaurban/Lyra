tc: int = int(input())

for t in range(1, tc+1):
    print("Case ")  # multi arg print
    print(t)
    print(":")
    n: int = int(input())  # n, p = map(int, input().split())
    p: int = int(input())
    reqs_str: List[str] = input().split()  # list(map(int, input().split()))
    reqs: List[int] = [0, 0, 0, 0, 0]
    for i in range(len(reqs_str)):
        reqs[i]: int = int(reqs_str[i])
    pls1: List[str] = input().split()
    pls2: List[str] = input().split()
    pls3: List[str] = input().split()
    for i in range(len(pls1)):
        pls1[i]: int = int(pls1[i])
    for i in range(len(pls2)):
        pls2[i]: int = int(pls2[i])
    for i in range(len(pls3)):
        pls3[i]: int = int(pls3[i])
    #TODO
    events = []
    for i in range(3):
        for j in range(p):
            # MAD: len(pls) > i => len(pls) > n-1 => n > n-1 => true
            # MAD: len(pls[i]) > j => forall elements x in pls: len(x) >= p
            u = pls[i][j]
            # MAD: len(reqs) > i => len(reqs) >= n
            req = reqs[i]
            # MAD: req != 0 because of ZeroDivison => all elements of reqs must be != 0 (until reqs[n-1])
            up = (10 * u) // (9 * req)
            # MAD: req != 0 because of ZeroDivison => all elements of reqs must be != 0 (until reqs[n-1])
            down = (10 * u + 11 * req - 1) // (11 * req)
            if down == 0: down = 1
            if up < down: continue
            events.append((down, False, i, u, j))
            events.append((up, True, i, u, j))
    events.sort()
    cnt = 0
    counts = [[] for _ in range(n)]
    remv = [0] * n
    for (bd, ev, i, yy, j) in events:
        if ev:
            if remv[i] > 0:
                remv[i] -= 1
            else:
                counts[i].remove(yy)
        else:
            counts[i].append(yy)
            if all(counts):
                cnt += 1
                for ii in range(n):
                    counts[ii].remove(min(counts[ii]))
                    remv[ii] += 1
    print(cnt)
