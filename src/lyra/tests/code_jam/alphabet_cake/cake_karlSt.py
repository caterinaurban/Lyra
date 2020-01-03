cases: int = int(input())
for case in range(1, (cases + 1)):
    rstr: str = (('Case #' + str(case)) + ': ')
    rc: List[str] = input().split()
    r: int = int(rc[0])
    c: int = int(rc[1])
    lines: List[List[str]] = []
    kids: Dict[(str, Tuple[(int, int)])] = {
        
    }
    for i in range(r):
        lines.append(list(input().rstrip()))
        for j in range(c):
            if (lines[i][j] != '?'):
                kids[lines[i][j]]: Tuple[(int, int)] = (i, j)
    for (kid, pos) in kids.items():
        top: int = pos[0]
        bot: int = pos[0]
        right: int = pos[1]
        left: int = pos[1]
        while (((top - 1) >= 0) and (lines[(top - 1)][pos[1]] == '?')):
            top -= 1
        while (((bot + 1) < r) and (lines[(bot + 1)][pos[1]] == '?')):
            bot += 1
        while ((right + 1) < c):
            check: bool = True
            for i in range(top, (bot + 1)):
                if (lines[i][(right + 1)] != '?'):
                    check: bool = False
            if (not check):
                break
            right += 1
        while ((left - 1) >= 0):
            check: bool = True
            for i in range(top, (bot + 1)):
                if (lines[i][(left - 1)] != '?'):
                    check: bool = False
            if (not check):
                break
            left -= 1
        for i in range(top, (bot + 1)):
            for j in range(left, (right + 1)):
                lines[i][j]: str = kid
    rstr += '\n'
    for line in lines:
        a_line: str = ''
        for index in range(len(line)):
            a_line += line[index]
        rstr += a_line + '\n'
    print(rstr)
