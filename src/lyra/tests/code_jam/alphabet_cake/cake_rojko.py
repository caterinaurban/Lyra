def fung(abec: List[str], g: List[List[str]], r: int, c: int) -> bool:
    dl: Dict[(str, int)] = {
        
    }
    dr: Dict[(str, int)] = {
        
    }
    db: Dict[(str, int)] = {
        
    }
    du: Dict[(str, int)] = {
        
    }
    for x in abec:
        dl[x]: int = c
        dr[x]: int = (- 1)
        du[x]: int = r
        db[x]: int = (- 1)
    for i in range(r):
        for j in range(c):
            x: str = g[i][j]
            dl[x]: int = min(dl[x], j)
            dr[x]: int = max(dr[x], j)
            du[x]: int = min(du[x], i)
            db[x]: int = max(db[x], i)
    for x in abec:
        zi: int = du[x]
        zj: int = dl[x]
        ki: int = db[x]
        kj: int = dr[x]
        kj += 1
        ki += 1
        i: int = zi
        j: int = zj
        while (i < ki):
            if (g[i][j] != g[zi][zj]):
                return False
            j += 1
            if (j == kj):
                i += 1
                j: int = zj
    return True

def rek(abec: List[str], g: List[List[str]], r: int, c: int, i: int, j: int) -> bool:
    if (i == r):
        return fung(abec, g, r, c)
    if (j == c):
        return rek(abec, g, r, c, (i + 1), 0)
    if (g[i][j] != '?'):
        return rek(abec, g, r, c, i, (j + 1))
    mam: bool = False
    for x in abec:
        g[i][j]: str = x
        ako: bool = rek(abec, g, r, c, i, (j + 1))
        if ako:
            mam: bool = True
            break
    if (not mam):
        g[i][j]: str = '?'
    return mam
T: int = int(input())
for t in range(1, (T + 1)):
    line: List[str] = input().split()
    r: int = int(line[0])
    c: int = int(line[1])
    g: List[List[str]] = []
    for i in range(r):
        a: str = input()
        g.append(list(a))
    print('Case #' + str(t) + ':')
    ab: Set[str] = set()
    for i in range(r):
        for j in range(c):
            if (g[i][j] == '?'):
                continue
            ab.add(g[i][j])
    abec: List[str] = list(ab)
    res: bool = rek(abec, g, r, c, 0, 0)
    for i in range(r):
        g_str: str = ''
        for index in range(len(g[i])):
            g_str += g[i][index]
        print(g_str)
