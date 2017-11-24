

_T:int = int(input())
t:int = 0
while t < _T:
    N:str = input()
    S:str = input()
    N:int = int(N)

    res:int = 0
    cur:int = 0
    i:int = 0
    while i < N+1:
        if i > cur:
            res:int = res +i - cur
            cur:int = i
        cur:int = cur + int(S)
        i:int = i+1
    t:int = t+1
