def flip(c: str) -> str:
    if (c == '+'):
        return '-'
    if (c == '-'):
        return '+'

def n_flip(cakes: str, n: int, idx: int) -> str:
    if (idx + n) > len(cakes):
        raise Exception
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
        first: int = cakes.find('-')
        cakes: str = n_flip(cakes, n, first)
        flips += 1
    if (cakes.count('-') == 1):
        return (- 1)
    if (not ('-' in cakes)):
        return flips
    raise IOError(cakes)

num_cases: int = int(input())
for i in range(num_cases):
    line: str = input()
    split_line: List[str] = line.split()
    cakes: str = split_line[0]
    flipper: int = int(split_line[1].strip())
    try:
        number: int = solve(cakes, flipper)
        if (number == (- 1)):
            result: str = 'IMPOSSIBLE'
        else:
            result: int = number
    except Exception:
        result: str = 'IMPOSSIBLE'
    print('Case #' + str(i + 1) + ': ' + str(result))
