T: int = int(input())
#for tt in range(T):
for tt in range(3):
    N: int = int(input())
    times: List[int] = [0, 0, 0]
    #for i in range(2*N-1):
    for i in range(5):
        info: List[int] = [0, 0, 0]
        info[0]: int = int(input())
        info[1]: int = int(input())
        # len(info) > 3
        info[2]: int = int(input())
        for x in info:
            if x not in times:
                times[x]: int = 1
            else:
                times[x]: int = times[x] + 1
    ans: int = 0
    for i in range(3):
        x: int = times[i]
        if times[x] / 2 == 1:
            ans: int = x

    print("Case #")
    print(tt+1)
    print(": ")
    print(ans)
    print("\n")
