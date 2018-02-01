
t: int = int(input())  # rewritten input into t
for i in range(1, t + 1):
    s_str: str = input()  # instead of s, k = input().split()
    k_str: str = input()
    print(s_str)
    print(k_str)
    k: int = int(k_str)
    # loop instead of list comprehension
    s: List[bool] = [False, False, False]
    for j in range(len(s_str)):
        s[i]: bool = s_str[i] == '+'
    flips: int = 0
    for i in range(len(s) - k + 1):
        if not s[i]:
            flips: int = flips + 1  # instead of +=
            for j in range(i, i + k):
                s[j]: bool = not s[j]
    all_s: bool = True  # instead of run_test: int = flips if all(s) else "IMPOSSIBLE"
    for c in s:
        if not c:
            all_s: bool = False
    if all_s:
        run_test: int = flips
    else:
        run_test: str = "IMPOSSIBLE"
    print("Case #")  #inlined method call, rewritten multi argument print
    print(i)
    print(": ")
    print(run_test)
