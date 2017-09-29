def sol(n, f):
    # MAD: input has to exist as integer (n)
    vis = [0] * n
    res = 0

    def dfs(i, l):
        if vis[i]:
            r = l - vis[i]
        else:
            vis[i] = l
            r = dfs(f[i], l + 1)
        vis[i] = 2 * n
        return r

    for i in xrange(n):
        if not vis[i]:
            res = max(dfs(i, 1), res)

    def lc(i, ii):
        q = [i]
        l = [0] * n
        for x in q:
            for j, k in enumerate(f):
                if k == x and j != ii:
                    q.append(j)
                    # MAD: if j != ii:
                    # MAD: len(l) > max(x) for k == x
                    # MAD: => len(l) > any value in q that is also in f
                    # MAD: => len(l) > i if i in f and len(l) > elements of f where j == k
                    l[j] = l[x] + 1
        return max(l)

    np = 0
    for j, i in enumerate(f):
        # MAD: len(f) > max(i) => len(f) > any value inf f
        if f[i] == j and j < i:
            np += lc(i, j) + lc(j, i) + 2

    return max(res, np)

rl = lambda: map(int, raw_input().split())

t = input()
# MAD: input has to exist as integer (t)
# MAD: t >= 1, otherwise no output
for i in xrange(t):
    n = input()
    # MAD: inputs have to exist as integers separated by whitespace
    f = [x - 1 for x in rl()]
    print("Case #%d:" % (i + 1), sol(n, f))
