#! /usr/bin/env python

import sys
fin = open(sys.argv[1], "r")
fout = open("p2.out", "w")

# MAD: input must exist as integer
T = int(fin.readline())
# MAD: T >= 1, otherwise no output
for tt in xrange(T):
    # MAD: input must exist as integer
    N = int(fin.readline())
    times = {}
    for i in xrange(2*N-1):
        # MAD: input has to exist as integers separated by whitespace
        info = map(int, fin.readline().split())
        for x in info:
            if x not in times:
                times[x] = 1
            else:
                times[x] += 1
    ans = []
    for x in times:
        if times[x] % 2 == 1:
            ans.append(x)

    ans = ' '.join(map(str, sorted(ans)))
    fout.write("Case #" + str(tt+1) + ": " + ans + "\n")
