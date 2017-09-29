# MAD: input has to exist as integer
t = int(input())

# MAD: t >= 1, otherwise no output
for tc in range(1, t + 1):
    print("Case #" + str(tc) + ": ", end = "")
    # MAD: input has to exist as two integers separated by whitespace
    line, k = input().strip().split()
    # MAD: input has to exist as integer
    k = int(k)
    line = [c == "+" for c in line]
    r = 0
    for i in range(len(line) - k + 1):
        # MAD: len(line) > max(i) => len(line) > len(line) - k + 1 - 1 => len(line) > len(line) - k => k > 0
        if not line[i]:
            r += 1
            for j in range(k):
                line[i+j] = not line[i+j]
    if all(line):
        print(r)
    else:
        print("IMPOSSIBLE")
