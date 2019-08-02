
from typing import Tuple, Dict, Sequence

def parseInputFrom(line: Sequence) -> Tuple[(int, int)]:
    spl: Dict[(int, None)] = line.split(' ')
    faces: int = 0
    for (idx, x) in enumerate(spl[0]):
        if (x != '+'):
            faces += (1 << idx)
    size: int = int(spl[1])
    return (faces, size)

def solve(faces: int, size: int) -> int:
    n: int = 0
    m: int = ((1 << size) - 1)
    while ((faces >= m) and (n < 10)):
        faces: int = (faces ^ (m << (faces.bit_length() - size)))
        n += 1
    if (faces == 0):
        return n
    return None

def represent(i: object, res: object) -> str:
    return ((('Case #' + str(i)) + ': ') + ('IMPOSSIBLE' if (res is None) else str(res)))
with open('input.1.in') as f:
    with open('output.1.txt', 'w') as f2:
        n: int = int(f.readline())
        i: int = 1
        line: Sequence = f.readline()
        while (line and (i <= n)):
            print(i, '/', n)
            (faces, size) = parseInputFrom(line)
            res: int = solve(faces, size)
            f2.write((represent(i, res) + '\n'))
            i += 1
            line: Sequence = f.readline()
