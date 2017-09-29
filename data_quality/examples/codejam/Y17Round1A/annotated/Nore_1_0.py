# MAD: input must exist as integer
tc = int(input())

# MAD: tc >= 1, otherwise no output
for t in range(1, tc+1):
    print("Case #%d: "%t, end = "")
    # MAD: input must be two integers separated by whitespace
    n, p = map(int, input().split())
    # MAD: inputs have to exist as integers separated by whitespace
    reqs = list(map(int, input().split()))
    pls = []
    for _ in range(n):
        pls.append(list(map(int, input().split())))
    events = []
    for i in range(n):
        for j in range(p):
            # MAD: len(pls[i]) > max(j) => n > p
            u = pls[i][j]
            # MAD: len(reqs) > max(i) => len(reqs) > n
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
