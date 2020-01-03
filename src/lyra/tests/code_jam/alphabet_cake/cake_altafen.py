def valid(cake_arg: List[List[str]]) -> bool:
    cake: List[List[str]] = list()
    for c in cake_arg:
        cake.append(c[:])
    seen: str = ''
    for x in range(len(cake)):
        for y in range(len(cake[0])):
            if (cake[x][y] == '?'):
                raise Exception
            elif (cake[x][y] == '_'):
                continue
            elif (cake[x][y] in seen):
                return False
            letter: str = cake[x][y]
            seen += letter
            for x2 in range(x, (len(cake) + 1)):
                if (x2 == len(cake)):
                    break
                if (cake[x][y] != cake[x2][y]):
                    break
            for y2 in range(y, (len(cake[0]) + 1)):
                if (y2 == len(cake[0])):
                    break
                if (cake[x][y] != cake[x][y2]):
                    break
            for x3 in range(x, x2):
                for y3 in range(y, y2):
                    if (cake[x3][y3] != letter):
                        return False
                    cake[x3][y3]: str = '_'
    return True

def solve(cake: List[List[str]]) -> List[List[str]]:
    letters: str = ''
    unk: List[Tuple[(int, int)]] = []
    for x in range(len(cake)):
        for y in range(len(cake[0])):
            if (cake[x][y] == '?'):
                unk.append((x, y))
            else:
                letters += cake[x][y]
    for attempt in product(letters, repeat=len(unk)):
        for (a, b) in zip(unk, attempt):
            cake[a[0]][a[1]]: str = b
        if valid(cake):
            return cake
    return [['WTF']]
T: int = int(input())
for case in range(T):
    line: List[str] = input().split()
    R: int = int(line[0])
    C: int = int(line[1])
    cake: List[List[str]] = []
    for row in range(R):
        cake.append(list(input()))
    print('Case #' + str(case + 1) + ': ')
    result: List[List[str]] = solve(cake)
    for index in range(len(result)):
        print(result[index])
