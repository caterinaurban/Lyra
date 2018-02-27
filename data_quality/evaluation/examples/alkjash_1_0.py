# Analysis finds [int]
# Manually: [int,

from typing import List

T: int = int(input())  # input instead of readline
for tt in range(T):
    N: int = int(input())
    times: List[int] = [0, 0, 0]  # instead of {}
    for i in range(N+N-1):
        info_str: List[str] = input().split()
        info: List[int] = [0, 0, 0]
        for i in range(len(info_str)):
            info[i]: int = int(info_str[i])  # instead of map(int, input().split())
        for x in info:
            if x not in times:
                times[x]: int = 1
            else:
                times[x]: int = times[x] + 1
    ans: List[int] = [0, 0, 0]
    for i in range(len(times)):
        x: int = times[i]
        if times[x] - 2 == 1:  # instead of if times[x] % 2 == 1:
            ans[i]: int = x  # instead of append


    print("Case #")
    print(tt+1)
    print(": ")
    #ans: List[int] = sorted(ans)
    for i in range(len(ans)):
        print(ans[i])
    print(ans)
    print("\n")
