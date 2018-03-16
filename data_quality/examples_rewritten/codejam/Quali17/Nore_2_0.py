# MAD: input has to exist as integer
t = int(input())

# MAD: t >= 1, otherwise no output
for tc in range(1, t + 1):
    print("Case #" + str(tc) + ": ", end = "")
    # MAD: input has to exist as two integers separated by whitespace
    n, k = map(int, input().split())
    d = {n: 1}
    lastc = None
    while k > 0:
        c = max(d)
        lastc = c
        d[(c - 1)//2] = d.get((c - 1)//2, 0) + d[c]
        d[c//2] = d.get(c//2, 0) + d[c]
        k -= d[c]
        del d[c]
    # MAD: lastc must be a value => lastc cannot be None => k > 0 to get into while loop and assign lastc
    print(lastc // 2, (lastc - 1) // 2)
