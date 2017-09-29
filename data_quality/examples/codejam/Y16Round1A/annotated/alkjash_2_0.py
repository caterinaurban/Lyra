#! /usr/bin/env python

import sys
fin = open(sys.argv[1], "r")
fout = open("p3.out", "w")

# MAD: input has to exist as integer
T = int(fin.readline())
# MAD: T >= 1, otherwise no output
for tt in xrange(T):
    N = int(fin.readline())
    # MAD: input has to exist as integers separated by whitespace
    out = map(int, fin.readline().split())
    out = map(lambda x: x-1, out)

    ans = 0

    best = [0 for j in xrange(N)]
    for i in xrange(N):
        cur = i
        vis = [0 for j in xrange(N)]
        vis[cur] = 1
        # MAD: len(out) > max(cur) => len(out) > N - 1
        # MAD: len(vis) > max(out[cur]) => N > any value in out (until out[N-1])
        while vis[out[cur]] == 0:
            vis[out[cur]] = 1
            cur = out[cur]
        if out[cur] == i:
            ans = max(ans, sum(vis))

        # MAD: len(out) > max(out[cur]) => len(out) > any value in out (until out[N-1])
        if out[out[cur]] == cur:
            best[cur] = max(best[cur], sum(vis))

    tot = 0
    for i in xrange(N):
        # MAD: len(out) > max(i) => len(out) > N - 1
        # MAD: len(out) > max(out[i]) => len(out) > any value in out (until out[N-1])
        if out[out[i]] == i:
            # MAD: len(best) > max(out[i]) => len(best) > any value in out (until out[N-1])
            tot += best[i] + best[out[i]] - 2

    tot /= 2
    ans = max(ans, tot)

    fout.write("Case #" + str(tt+1) + ": " + str(ans) + "\n")
