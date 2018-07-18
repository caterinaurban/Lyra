
import numpy as np


def solve():
    n = int(input())
    a = map(int, input().split())
    best = np.inf
    for m in range(1, max(a) + 1):
        t = 0
        for ai in a:
            t += (ai - 1) // m
        if m + t < best:
            best = m + t
    print(best)


if __name__ == '__main__':
    T = int(input())
    for t in range(T):
        print ('Case #{0}:'.format(t + 1),
        solve())