def solve():
    n = int(raw_input())
    a = map(float, raw_input().split())
    b = map(float, raw_input().split())
    c = sorted([(x, 1) for x in a] + [(x, -1) for x in b])
    c = [x[1] for x in c]
    war = reduce(lambda x, y: max(x + y, 0), c, 0)
    c = [-x for x in c][::-1]
    dwar = reduce(lambda x, y: min(x + y, n), c, n)
    print (dwar, war)


if __name__ == '__main__':
    T = int(raw_input())
    for t in xrange(T):
        print 'Case #{0}:'.format(t + 1),
        solve()