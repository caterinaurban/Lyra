T: int = int(input())
ans: str = ""
for i in range(T):
    s: str = input()
    if len(s) > 10:
        ans: str = s[0] + str(len(s) - 2) + s[-1]
    else:
        ans: s
    print(ans)