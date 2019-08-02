
from typing import IO, List, Sequence, Tuple
inputF: IO = open('C-small-attempt0.in', 'r')
output: IO = open('C-small-attempt0.out', 'w')
numCases: int = int(inputF.readline())

def checkConfig(houseConfig: object) -> None:
    r: int = len(houseConfig)
    c: int = len(houseConfig[0])
    locks: List[List[object]] = [(['.'] * c) for i in range(r)]
    for i in range(r):
        for j in range(c):
            if ((houseConfig[i][j] == '-') or (houseConfig[i][j] == '|')):
                horizontalCollide: int = False
                for k in range((j - 1), (- 1), (- 1)):
                    char: Sequence = houseConfig[i][k]
                    if (char == '#'):
                        break
                    elif ((char == '|') or (char == '-')):
                        horizontalCollide: int = True
                        break
                for k in range((j + 1), c):
                    char: Sequence = houseConfig[i][k]
                    if (char == '#'):
                        break
                    elif ((char == '|') or (char == '-')):
                        horizontalCollide: int = True
                        break
                verticalCollide: int = False
                for k in range((i - 1), (- 1), (- 1)):
                    char: Sequence = houseConfig[k][j]
                    if (char == '#'):
                        break
                    elif ((char == '|') or (char == '-')):
                        verticalCollide: int = True
                        break
                for k in range((i + 1), r):
                    char: Sequence = houseConfig[k][j]
                    if (char == '#'):
                        break
                    elif ((char == '|') or (char == '-')):
                        verticalCollide: int = True
                        break
                if (horizontalCollide and verticalCollide):
                    return False
                elif horizontalCollide:
                    locks[i][j]: object = '|'
                elif verticalCollide:
                    locks[i][j]: object = '-'
    for i in range(r):
        for j in range(c):
            if (((houseConfig[i][j] == '-') or (houseConfig[i][j] == '|')) and (locks[i][j] != '.')):
                houseConfig[i][j]: object = locks[i][j]
                if (locks[i][j] == '-'):
                    for k in range((j - 1), (- 1), (- 1)):
                        char: Sequence = houseConfig[i][k]
                        if (char == '#'):
                            break
                        elif (char == '.'):
                            houseConfig[i][k]: object = 'C'
                    for k in range((j + 1), c):
                        char: Sequence = houseConfig[i][k]
                        if (char == '#'):
                            break
                        elif (char == '.'):
                            houseConfig[i][k]: object = 'C'
                else:
                    for k in range((i - 1), (- 1), (- 1)):
                        char: Sequence = houseConfig[k][j]
                        if (char == '#'):
                            break
                        elif (char == '.'):
                            houseConfig[k][j]: object = 'C'
                    for k in range((i + 1), r):
                        char: Sequence = houseConfig[k][j]
                        if (char == '#'):
                            break
                        elif (char == '.'):
                            houseConfig[k][j]: object = 'C'
    updateMade: int = True
    while updateMade:
        updateMade: int = False
        for i in range(r):
            for j in range(c):
                if (houseConfig[i][j] == '.'):
                    beamCount: int = 0
                    lockLoc: Tuple[(int, object, object)] = (0, 0)
                    for k in range((j - 1), (- 1), (- 1)):
                        char: Sequence = houseConfig[i][k]
                        if (char == '#'):
                            break
                        elif (((char == '|') or (char == '-')) and (locks[i][k] == '.')):
                            beamCount += 1
                            lockLoc: Tuple[(int, object, object)] = (i, k, '-')
                            break
                    for k in range((j + 1), c):
                        char: Sequence = houseConfig[i][k]
                        if (char == '#'):
                            break
                        elif (((char == '|') or (char == '-')) and (locks[i][k] == '.')):
                            beamCount += 1
                            lockLoc: Tuple[(int, object, object)] = (i, k, '-')
                            break
                    for k in range((i - 1), (- 1), (- 1)):
                        char: Sequence = houseConfig[k][j]
                        if (char == '#'):
                            break
                        elif (((char == '|') or (char == '-')) and (locks[k][j] == '.')):
                            beamCount += 1
                            lockLoc: Tuple[(int, object, object)] = (k, j, '|')
                            break
                    for k in range((i + 1), r):
                        char: Sequence = houseConfig[k][j]
                        if (char == '#'):
                            break
                        elif (((char == '|') or (char == '-')) and (locks[k][j] == '.')):
                            beamCount += 1
                            lockLoc: Tuple[(int, object, object)] = (k, j, '|')
                            break
                    if (beamCount == 0):
                        return False
                    elif (beamCount == 1):
                        updateMade: int = True
                        a: int = lockLoc[0]
                        b: int = lockLoc[1]
                        locks[a][b]: object = lockLoc[2]
                        houseConfig[a][b]: object = lockLoc[2]
                        if (locks[a][b] == '-'):
                            for k in range((b - 1), (- 1), (- 1)):
                                char: Sequence = houseConfig[a][k]
                                if (char == '#'):
                                    break
                                elif (char == '.'):
                                    houseConfig[a][k]: object = 'C'
                            for k in range((b + 1), c):
                                char: Sequence = houseConfig[a][k]
                                if (char == '#'):
                                    break
                                elif (char == '.'):
                                    houseConfig[a][k]: object = 'C'
                        else:
                            for k in range((a - 1), (- 1), (- 1)):
                                char: Sequence = houseConfig[k][b]
                                if (char == '#'):
                                    break
                                elif (char == '.'):
                                    houseConfig[k][b]: object = 'C'
                            for k in range((a + 1), r):
                                char: Sequence = houseConfig[k][b]
                                if (char == '#'):
                                    break
                                elif (char == '.'):
                                    houseConfig[k][b]: object = 'C'
    for i in range(r):
        for j in range(c):
            if (houseConfig[i][j] == 'C'):
                houseConfig[i][j]: object = '.'
            elif (((houseConfig[i][j] == '-') or (houseConfig[i][j] == '|')) and (locks[i][j] == '.')):
                houseConfig[i][j]: object = '-'
    s: str = ''
    for i in range(r):
        for j in range(c):
            s += houseConfig[i][j]
        s += '\n'
    return s
for i in range(numCases):
    (r, c) = inputF.readline().split()
    ticketCustomerPairs: object = []
    houseConfig: List[object] = []
    for j in range(int(r)):
        line: None = inputF.readline().strip()
        houseConfig += [list(line)]
    s: None = checkConfig(houseConfig)
    if (not s):
        output.write((('Case #' + str((i + 1))) + ': IMPOSSIBLE\n'))
    else:
        output.write((('Case #' + str((i + 1))) + ': POSSIBLE\n'))
        output.write(s)
inputF.close()
output.close()
