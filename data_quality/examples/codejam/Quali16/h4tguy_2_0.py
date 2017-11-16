def int2base(x, b):
    at = 1
    ans = 0
    for dig in x:
        ans += at * dig
        at *= b
    return ans


def get(n, j):
    res = []
    sub = n / 2
    divs = [str(i ** sub + 1) for i in range(2, 11)]
    for i in range(j):
        strdiv = ("1{0:0>" + str(sub - 2) + "b}1").format(i)
        res.append(strdiv + strdiv)
    return res, divs

# MAD: input has to exist as integer
t = int(input())
# MAD: input has to exist as two integers separated by whitespace
n, j = map(int, input().split())
res, divs = get(n, j)
print("Case #1:")
for i in res:
    print(i, " ".join(divs))
