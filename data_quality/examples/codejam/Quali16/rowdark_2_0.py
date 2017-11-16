# MAD: input has to exist as integer
T = int(input())
# MAD: no output if T <= 0
for tt in range(T):
    # MAD: input has to exist as two integers separated by whitespace
    N, J = map(int, input().strip().split());
    print("Case #" + str(tt + 1) + ":")
    f = 2 ** (N // 2) + 1
    base = 2 ** (N // 2 - 1) + 1
    gg = ""
    for i in range(2, 11):
        gg += " " + str(i ** (N // 2) + 1)
    for i in range(J):
        print(bin((base + i * 2) * f)[2:] + gg)

