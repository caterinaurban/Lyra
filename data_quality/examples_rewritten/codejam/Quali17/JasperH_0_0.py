
for i in range(1, int(input()) + 1):
    print("Case #")
    print(i)
    print(": ")
    s: str = input()
    k: int = int(input())
    print(s)
    print(k)
    new_s: List[bool] = [0, 0, 0]
    for i in range(len(s)):
        tmp_s[i]: bool = (s[i] == '+')
    flips: int = 0
    for i in range(len(new_s) - k + 1):
        if not new_s[i]:
            flips: int = flips + 1
            for j in range(i, i + k):
                new_s[j]: bool = not new_s[j]
    all_flips: bool = True
    for c in new_s:
        if not (c == True):
            all_flips: bool = False
    if all_flips == True:
        print(flips)
    else:
        print("IMPOSSIBLE")
