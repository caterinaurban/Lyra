#!python
# http://code.google.com/codejam/contest/dashboard?c=975485#s=p2
import sys
from optparse import OptionParser
from collections import deque
usage = "usage: %prog input"
parser = OptionParser(usage=usage)
(options, args) = parser.parse_args()
if args:
    if args[0] == "-":
        f = sys.stdin
    else:
        f = open(args[0])
elif not sys.stdin.isatty():
    f = sys.stdin
else:
    parser.error("Need input from file or stdin")

T = int(f.readline())

def psum(x,y):
    return x^y

for i in range(1,T+1):
    N = int(f.readline())
    candies = [ int(x) for x in f.readline().split()  ]
    if reduce(psum,candies) == 0:
        answer = sum(candies) - min(candies)
    else:
        answer = "NO"
    print "Case #%d: %s" % (i,answer)


#RE-WRITTEN

for i in range(T):
    N: int = int(input())
    candies_str: List[str] = input().split()
    candies_int: List[int] = [int(x) for x in candies_str]
    psum: int = 0
    for i in range(len(candies_int)):
        psum: int = psum ^ candies_int[i]

    sum_candies: int = 0
    min_candies: int = candies_int[0]
    for i range(len(candies_int)):
        sum_candies: int = sum_candies + candies_int[i]
        if min_candies > candies_int[i]:
            min_candies:int = candies_int[i]

    if psum == 0:
        answer = sum_candies - min_candies
    else:
        raise ValueError