tc: int = int(input())

for t in range(1, tc+1):
    print("Case #")
    print(t)
    print(":")
    n: int = int(input())
    p: int = int(input())

    req: int = int(input())

    pls: List[int] = [0, 1]
    for i in range(n):
        pls[i]: int = int(input())

    events1: int = 0
    events2: bool = False
    events3: int = 0
    events4: int = 0
    events5: int = 0
    events21: int = 0
    events22: bool = False
    events23: int = 0
    events24: int = 0
    events25: int = 0

    for i in range(n):
        for j in range(p):
            u: int = pls[i]
            up: int = (10 * u) // (9 * req)
            down: int = (10 * u + 11 * req - 1) // (11 * req)
            if down == 0:
                down: int = 1
            if up < down:
                continue
            events1: int = down
            events2: bool = False
            events3: int = i
            events4: int = u
            events5: int = j
            events21: int = up
            events22: bool = True
            events23: int = i
            events24: int = u
            events25: int = j
    cnt: int = 0
    counts: int = 0
    remv: int = 0
    if events2 == True:
        if remv > 0:
            remv: int = remv - 1
    else:
        counts: int = events4
        if counts != 0:
            cnt: int = cnt + 1
            for ii in range(n):
                remv: int = remv - 1
    print(cnt)
