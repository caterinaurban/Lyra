LINES_PARAM: int = 0

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
    parsed: List[List[str]] = list()
    for i in range(1, (R + 1)):
        for j in range(C):
            parsed.append([parsed[i][0][j]])
    for i in range(R):
        for j in range(C):
            if (parsed[i][j] == '-'):
                parsed[i][j]: str = '|'
    for i in range(R):
        for j in range(C):
            if (parsed[i][j] == '|'):
                beam_arg: List[str] = list()
                for k in range(R):
                    beam_arg.append(parsed[k][j])
                samecol: bool = seesBeam(beam_arg, i)
                if samecol:
                    if seesBeam(parsed[i], j):
                        return 'IMPOSSIBLE'
                    parsed[i][j]: str = '-'
    for t in range(((5 * C) + (5 * R))):
        for i in range(R):
            for j in range(C):
                if (parsed[i][j] == '.'):
                    sees_arg: List[str] = list()
                    for k in range(R):
                        sees_arg.append(parsed[k][j])
                    samecol: bool = seesVert(sees_arg, i)
                    if (not samecol):
                        k: int = findhor(parsed[i], j)
                        if (k == j):
                            return 'IMPOSSIBLE'
                        parsed[i][k]: str = '-'
    lines: str = ''
    for i in range(R):
        for j in range(len(parsed[i])):
            lines += parsed[i][j]
        lines += '\n'
    return 'POSSIBLE' + '\n' + lines

def do_parse(input: List[str]) -> List[List[str]]:
    result: List[List[str]] = list()
    for line in input:
        result.append(line.rstrip().split())
    return result

output: List[str] = []
num_of_test_cases: int = int(input())
temp: List[str] = input()
index: int = 0
for test_case in range(num_of_test_cases):
    lines: int = int(temp[index].rstrip().split()[LINES_PARAM])
    parsed_input: List[List[str]] = do_parse(temp[index:((index + lines) + 1)])
    index: int = ((index + 1) + lines)
    output.append(((('Case #' + str((test_case + 1))) + ': ') + do_case(parsed_input)))
for output_line in output:
    print(output_line)
