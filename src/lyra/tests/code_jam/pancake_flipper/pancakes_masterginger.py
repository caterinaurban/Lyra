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
        del queue[0]
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
        queue: List[str] = sorted(queue, key=(lambda p: table[p]))
    return m
T: int = int(input())
for i in range(0, T):
    segments: List[str] = input().split(' ')
    pattern: str = segments[0]
    K: int = int(segments[1])
    result: int = solve(pattern, K)
    if (result >= 0):
        print('Case #' + str(i + 1) + ': ' + str(result))
    else:
        print('Case #' + str(i + 1) + ': ' + 'IMPOSSIBLE')
