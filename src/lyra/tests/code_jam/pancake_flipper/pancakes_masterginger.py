def sort(queue: List[str], table: Dict[(str, int)]):
    elements: int = len(queue)
    for i in range(elements-1):
        for j in range(i+1, elements):
            index_i: int = table[queue[i]]
            index_j: int = table[queue[j]]
            if index_i > index_j:
                aux: str = queue[i]
                queue[i] = queue[j]
                queue[j] = aux

def ok(pattern: str) -> bool:
    c: str = ''
    for c in pattern:
        if (c != '+'):
            return False
    return True

def inversed(c: str) -> str:
    if (c == '+'):
        return '-'
    return '+'

def flip(pattern: str, start: int, K: int) -> str:
    ret: str = ''
    l: int = len(pattern)
    for i in range(0, l):
        if (i in range(start, (start + K))):
            ret += inversed(pattern[i])
        else:
            ret += pattern[i]
    return ret

def solve(pattern: str, K: int) -> int:
    table: Dict[(str, int)] = {
        
    }
    table[pattern]: int = 0
    queue: List[str] = [pattern]
    m: int = (- 1)
    while (len(queue) > 0):
        p: str = queue[0]
        queue = queue[1:]
        current: int = table[p]
        if ((m >= 0) and (current >= m)):
            break
        if ok(p):
            if ((m < 0) or (current < m)):
                m: int = current
            continue
        for i in range(0, ((len(pattern) - K) + 1)):
            flipped: str = flip(p, i, K)
            if (flipped not in table):
                table[flipped]: int = (current + 1)
            elif (table[flipped] > (current + 1)):
                table[flipped]: int = (current + 1)
            else:
                continue
            queue.append(flipped)
        sort(queue, table)
    return m
T: int = int(input())
for i in range(0, T):
    segments: List[str] = input().split()
    pattern: str = segments[0]
    K: int = int(segments[1])
    result: int = solve(pattern, K)
    case_number: int = i + 1
    if (result >= 0):
        print('Case #' + str(case_number) + ': ' + str(result))
    else:
        print('Case #' + str(case_number) + ': ' + 'IMPOSSIBLE')
