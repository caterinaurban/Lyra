
from typing import List, Dict, Callable, Set
T: int = int(input())
for K in range(T):
    (n, m) = [int(g) for g in input().split(' ')]
    plusMap: Dict[(object, Dict[(object, object)])] = [(['.'] * n) for i in range(n)]
    xMap: List[List[object]] = [(['.'] * n) for i in range(n)]
    plusMark: List[List[int]] = []
    xMark: List[object] = []
    xRow: None = set(range(n))
    xCol: None = set(range(n))
    ans: int = 0
    for i in range(m):
        (s, r, c) = [g for g in input().split(' ')]
        r: int = int(r)
        c: int = int(c)
        if (s in ['+', 'o']):
            plusMark.append([r, c])
            ans += 1
        if (s in ['x', 'o']):
            xMark.append([r, c])
            xRow.remove((r - 1))
            xCol.remove((c - 1))
            ans += 1
    leftToRight: Callable[([int], int)] = (lambda left: ((min((left - 1), n) * 2) - left))
    rightToLeft: List[None] = []
    for i in range(n):
        rightToLeft.append(set([(i + 2), ((2 * n) - i)]))
    if (len(rightToLeft) > 1):
        rightToLeft[0].pop()
    rightCount: Set[int] = set([])
    for plus in plusMark:
        [r, c] = plus
        left: int = (r + c)
        right: int = abs((r - c))
        rightCount.add((r - c))
        if (leftToRight(left) > right):
            rightToLeft[right].pop()
        right: int = leftToRight(left)
        if (right == 0):
            rightToLeft[0].pop()
        else:
            rightToLeft[leftToRight(left)].remove(left)
    for i in range(n):
        right: None = rightToLeft[i]
        if (len(right) == 2):
            l: complex = right.pop()
            r: int = i
            plusMap[(((l + r) / 2) - 1)][(((l - r) / 2) - 1)]: object = '+'
            ans += 1
            l: complex = right.pop()
            r: int = (- i)
            plusMap[(((l + r) / 2) - 1)][(((l - r) / 2) - 1)]: object = '+'
            ans += 1
        elif (len(right) == 1):
            l: complex = right.pop()
            if (i in rightCount):
                r: int = (- i)
            else:
                r: int = i
            plusMap[(((l + r) / 2) - 1)][(((l - r) / 2) - 1)]: object = '+'
            ans += 1
    xMap: List[List[object]] = [(['.'] * n) for i in range(n)]
    while (len(xRow) > 0):
        xMap[xRow.pop()][xCol.pop()]: object = 'x'
        ans += 1
    count: int = 0
    s: str = ''
    for i in range(n):
        for j in range(n):
            if ((plusMap[i][j] == '+') and (xMap[i][j] == 'x')):
                count += 1
                s += ((('\no ' + str((i + 1))) + ' ') + str((j + 1)))
            elif (plusMap[i][j] == '+'):
                if ([(i + 1), (j + 1)] in xMark):
                    s += '\no '
                else:
                    s += '\n+ '
                count += 1
                s += ((str((i + 1)) + ' ') + str((j + 1)))
            elif (xMap[i][j] == 'x'):
                if ([(i + 1), (j + 1)] in plusMark):
                    s += '\no '
                else:
                    s += '\nx '
                count += 1
                s += ((str((i + 1)) + ' ') + str((j + 1)))
    print('Case #{}: {} {}'.format((K + 1), ans, count))
    if (count > 0):
        print(s.strip('\n'))
