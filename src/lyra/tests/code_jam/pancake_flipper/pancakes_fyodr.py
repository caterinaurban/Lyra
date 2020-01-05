def check(memos: Dict[(Tuple[(int, int, int, int)], int)], i: int, s: int, c: int, k: int) -> int:
    if (s == 0):
        return 0
    elif ((i, s, c, k) not in memos):
        memos[(i, s, c, k)]: int = (- 1)
        flip: int = 0
        for j in range(k):
            flip += (1 << j)
        flip: int = (flip << i)
        new_s: int = (s ^ flip)
        best: int = (- 1)
        for j in range((c - (k - 1))):
            maybe: int = check(j, new_s, c, k)
            if (maybe == 0):
                best: int = maybe
                break
            elif (maybe == (- 1)):
                pass
            elif ((best == (- 1)) or (maybe < best)):
                best: int = maybe
        if (best == (- 1)):
            memos[(i, s, c, k)]: int = best
        else:
            memos[(i, s, c, k)]: int = (best + 1)
    return memos[(i, s, c, k)]


T: int = int(input().strip())
lines: List[str] = []
memos: Dict[(Tuple[(int, int, int, int)], int)] = {

}
for t in range(1, (T + 1)):
    line: List[str] = input().strip().split()
    cakes: str = line[0]
    k: int = int(line[1])
    s: int = 0
    for i in range(len(cakes)):
        c: str = cakes[i]
        if (c == '-'):
            s += (1 << i)
    best: int = (- 1)
    for i in range((len(cakes) - (k - 1))):
        maybe: int = check(memos, i, s, len(cakes), k)
        if (maybe == 0):
            best: int = maybe
            break
        if (maybe == (- 1)):
            pass
        elif ((maybe < best) or (best == (- 1))):
            best: int = maybe
    if (best == (- 1)):
        lines.append('Case #' + str(t) + ': ' + 'IMPOSSIBLE')
    else:
        lines.append('Case #' + str(t) + ': ' + str(best))
    print(lines[(- 1)])
