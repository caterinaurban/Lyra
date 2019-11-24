
from typing import IO, List
LINES_PARAM: int = 0
INPUT_FILE_NAME: str = 'C-small-attempt4.in'
OUTPUT_FILE_NAME: str = 'C-small-attempt4.out'

def findhor(a: List[str], i: int) -> int:
    seen: bool = False
    k: int = i
    vis: bool = True
    for j in range((i + 1), len(a)):
        if (((a[j] == '|') or (a[j] == '-')) and vis):
            if seen:
                return i
            k: int = j
            seen: bool = True
        if (a[j] == '#'):
            vis: bool = False
    vis: bool = True
    for j in range((i - 1), (- 1), (- 1)):
        if (((a[j] == '|') or (a[j] == '-')) and vis):
            if seen:
                return i
            k: int = j
            seen: bool = True
        if (a[j] == '#'):
            vis: bool = False
    return k

def seesVert(a: List[str], i: int) -> bool:
    vis: bool = True
    for j in range((i + 1), len(a)):
        if ((a[j] == '|') and vis):
            return True
        if (a[j] == '#'):
            vis: bool = False
    vis: bool = True
    for j in range((i - 1), (- 1), (- 1)):
        if ((a[j] == '|') and vis):
            return True
        if (a[j] == '#'):
            vis: bool = False
    return False

def seesBeam(a: List[str], i: int) -> bool:
    vis: bool = True
    for j in range((i + 1), len(a)):
        if (((a[j] == '|') or (a[j] == '-')) and vis):
            return True
        if (a[j] == '#'):
            vis: bool = False
    vis: bool = True
    for j in range((i - 1), (- 1), (- 1)):
        if (((a[j] == '|') or (a[j] == '-')) and vis):
            return True
        if (a[j] == '#'):
            vis: bool = False
    return False

def do_case(parsed: List[List[str]]) -> str:
    R: int = int(parsed[0][0])
    C: int = int(parsed[0][1])
    parsed: List[List[str]] = [[parsed[i][0][j] for j in range(C)] for i in range(1, (R + 1))]
    for i in range(R):
        for j in range(C):
            if (parsed[i][j] == '-'):
                parsed[i][j]: str = '|'
    for i in range(R):
        for j in range(C):
            if (parsed[i][j] == '|'):
                samecol: bool = seesBeam([parsed[k][j] for k in range(R)], i)
                if samecol:
                    if seesBeam(parsed[i], j):
                        return 'IMPOSSIBLE'
                    parsed[i][j]: str = '-'
    for t in range(((5 * C) + (5 * R))):
        for i in range(R):
            for j in range(C):
                if (parsed[i][j] == '.'):
                    samecol: bool = seesVert([parsed[k][j] for k in range(R)], i)
                    if (not samecol):
                        k: int = findhor(parsed[i], j)
                        if (k == j):
                            return 'IMPOSSIBLE'
                        parsed[i][k]: str = '-'
    lines: List[str] = [''.join(parsed[i]) for i in range(R)]
    return '\n'.join(['POSSIBLE', '\n'.join(lines)])

def do_parse(input: List[str]) -> List[List[str]]:
    return [line.rstrip().split(' ') for line in input]

def main() -> None:
    input_f: IO = open(INPUT_FILE_NAME, 'r')
    output: List[str] = []
    num_of_test_cases: int = int(input_f.readline(), 10)
    temp: List[str] = input_f.readlines()
    index: int = 0
    for test_case in range(num_of_test_cases):
        lines: int = int(temp[index].rstrip().split(' ')[LINES_PARAM])
        parsed_input: List[List[str]] = do_parse(temp[index:((index + lines) + 1)])
        index: int = ((index + 1) + lines)
        output.append(((('Case #' + str((test_case + 1))) + ': ') + do_case(parsed_input)))
    output_f: IO = open(OUTPUT_FILE_NAME, 'w')
    output_f.write('\n'.join(output))
    input_f.close()
    output_f.close()
if (__name__ == '__main__'):
    main()
