def run_test():
    # MAD: input has to exist as two values separated by whitespace
    s, k = input().split()
    print(s)
    print(k)
    # MAD: input has to exist as integer
    k = int(k)
    s = [c == '+' for c in s]
    flips = 0
    for i in range(len(s) - k + 1):
        # MAD: len(s) > max(i) => len(s) > len(s) - k + 1 - 1 => len(s) > len(s) - k => k > 0
        if not s[i]:
            flips += 1
            for j in range(i, i + k):
                s[j] = not s[j]
    return flips if all(s) else "IMPOSSIBLE"

# MAD: input has to exist as integer
# MAD: no output if input < 1
for i in range(1, int(input()) + 1):
    print("Case #{}: {}".format(i, run_test()))
