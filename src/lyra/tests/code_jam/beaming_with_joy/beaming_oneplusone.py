
from typing import Dict, List, Sequence, Tuple
inname: str = 'input.txt'
outname: Sequence = 'output.txt'
with open(inname, 'r') as f:
    cases: int = int(f.readline())
    for tc in range(1, (cases + 1)):
        line: str = f.readline().strip().split(' ')
        R: int = int(line[0])
        C: int = int(line[1])
        grid: List[List[int]] = []
        cells: List[Dict[(int, List[Tuple[(int, int)]])]] = []
        lasers: List[List[Tuple[(int, int)]]] = []
        for i in range(R):
            grid.append(([0] * C))
            cells.append(([0] * C))
            line: str = f.readline().strip()
            for j in range(C):
                if (line[j] == '.'):
                    grid[i][j]: int = 0
                    cells[i][j]: List[Tuple[(int, int)]] = []
                elif (line[j] == '#'):
                    grid[i][j]: int = 1
                elif ((line[j] == '|') or (line[j] == '-')):
                    grid[i][j]: int = 2
                    lasers.append([(i, j), 0])
        L: int = len(lasers)
        possible: complex = True
        rules: List[Tuple[(int, int)]] = []
        for i in range(L):
            (r, c) = lasers[i][0]
            rr: int = (r - 1)
            while (rr >= 0):
                if (grid[rr][c] == 0):
                    cells[rr][c].append((i, 2))
                elif (grid[rr][c] == 1):
                    break
                else:
                    rules.append((i, 1))
                rr -= 1
            rr: int = (r + 1)
            while (rr < R):
                if (grid[rr][c] == 0):
                    cells[rr][c].append((i, 2))
                elif (grid[rr][c] == 1):
                    break
                else:
                    rules.append((i, 1))
                rr += 1
            cc: int = (c - 1)
            while (cc >= 0):
                if (grid[r][cc] == 0):
                    cells[r][cc].append((i, 1))
                elif (grid[r][cc] == 1):
                    break
                else:
                    rules.append((i, 2))
                cc -= 1
            cc: int = (c + 1)
            while (cc < C):
                if (grid[r][cc] == 0):
                    cells[r][cc].append((i, 1))
                elif (grid[r][cc] == 1):
                    break
                else:
                    rules.append((i, 2))
                cc += 1
        finallaser: List[int] = ([0] * L)
        for i in range(len(rules)):
            (l, d) = rules[i]
            if (finallaser[l] == 0):
                finallaser[l]: int = d
            else:
                possible: complex = False
                break
        for r in range(R):
            for c in range(C):
                if (cells[r][c] != 0):
                    if (len(cells[r][c]) == 0):
                        possible: complex = False
                        break
                    elif (len(cells[r][c]) == 1):
                        (l, d) = cells[r][c][0]
                        if ((finallaser[l] > 0) and (finallaser[l] != d)):
                            possible: complex = False
                            break
                        else:
                            finallaser[l]: int = d
        for r in range(R):
            for c in range(C):
                if ((cells[r][c] != 0) and (len(cells[r][c]) == 2)):
                    (l1, d1) = cells[r][c][0]
                    (l2, d2) = cells[r][c][1]
                    if (finallaser[l1] == 0):
                        finallaser[l1]: int = d1
                    elif (finallaser[l1] == d1):
                        pass
                    elif (finallaser[l2] == 0):
                        finallaser[l2]: int = d2
                    elif (finallaser[l2] == d2):
                        pass
                    else:
                        possible: complex = False
                        break
        if (not possible):
            print(('Case #%d: IMPOSSIBLE' % tc))
        else:
            finalgrid: List[List[str]] = []
            for i in range(R):
                finalgrid.append((['.'] * C))
                for j in range(C):
                    if (grid[i][j] == 0):
                        finalgrid[i][j]: str = '.'
                    elif (grid[i][j] == 1):
                        finalgrid[i][j]: str = '#'
            for i in range(L):
                d: int = finallaser[i]
                if (d == 0):
                    d: int = 1
                (r, c) = lasers[i][0]
                if (d == 1):
                    finalgrid[r][c]: str = '-'
                else:
                    finalgrid[r][c]: str = '|'
            print(('Case #%d: POSSIBLE' % tc))
            for i in range(R):
                print(''.join(finalgrid[i]))
