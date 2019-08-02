
from typing import Sequence
FAIL: None = 'IMPOSSIBLE'

def flip(c: Sequence) -> str:
    if (c == '+'):
        return '-'
    if (c == '-'):
        return '+'

def n_flip(cakes: str, n: int, idx: int) -> str:
    assert ((idx + n) <= len(cakes))
    to_return: str = cakes[:idx]
    for i in range(n):
        to_return += flip(cakes[(idx + i)])
    to_return += cakes[(idx + n):]
    return to_return

def solve(cakes: str, n: int) -> int:
    if (not ('-' in cakes)):
        return 0
    flips: int = 0
    idx: int = 0
    while ((('-' in cakes) or (cakes.count('-') == 1)) and (idx < 10)):
        idx += 1
        first: None = cakes.find('-')
        cakes: str = n_flip(cakes, n, first)
        flips += 1
    if (cakes.count('-') == 1):
        return FAIL
    if (not ('-' in cakes)):
        return flips
    raise IOError(cakes)
with open('A-small-attempt0.in') as f:
    num_cases: int = int(f.readline())
    for i in range(num_cases):
        line: str = f.readline()
        cakes: str = line.split(' ')[0]
        flipper: int = int(line.split(' ')[1].strip())
        try:
            result: complex = solve(cakes, flipper)
        except Exception:
            result: complex = FAIL
        print('Case #{}: {}'.format((i + 1), result))
