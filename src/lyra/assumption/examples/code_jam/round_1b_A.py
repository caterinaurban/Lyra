import numpy as np


def split(s):
    chars, counts = [], []
    cur_char, cur_count = None, 0
    for c in s:
        if cur_char is None:
            cur_char = c
            cur_count = 1
        elif cur_char == c:
            cur_count += 1
        else:
            chars.append(cur_char)
            counts.append(cur_count)
            cur_char = c
            cur_count = 1
    chars.append(cur_char)
    counts.append(cur_count)
    return (chars, counts)


def equalize(a):
    a.sort()
    return sum(abs(a - a[len(a) // 2]))


def solve():
    n = int(raw_input())
    strings = [raw_input().strip() for __ in xrange(n)]
    chars, counts = [], []
    for s in strings:
        ret = split(s)
        chars.append(ret[0])
        counts.append(ret[1])
        if len(chars) >= 2 and chars[-1] != chars[-2]:
            print 'Fegla Won'
            return

    counts = np.asarray(counts)
    print sum(equalize(counts[:, i]) for i in xrange(counts.shape[1]))
