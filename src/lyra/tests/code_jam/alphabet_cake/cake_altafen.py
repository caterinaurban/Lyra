def valid(cake_arg: List[List[str]]) -> bool:
    cake: List[List[str]] = list()
    for c in cake_arg:
        cake.append(c[:])
    seen: str = ''
    for x in range(len(cake)):
        first: str = cake[0]
        for y in range(len(first)):
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
            for y2 in range(y, (len(first) + 1)):
                if (y2 == len(first)):
                    break
                if (cake[x][y] != cake[x][y2]):
                    break
            for x3 in range(x, x2):
                for y3 in range(y, y2):
                    if (cake[x3][y3] != letter):
                        return False
                    cake[x3][y3]: str = '_'
    return True

def cartesian_product(inputs: List[List[str]]) -> List[List[str]]:
    solutions: int = 1
    for an_input in inputs:
        solutions *= len(an_input)

    product: List[List[str]] = list()
    for i in range(solutions):
        j: int = 1
        result_line: str = ''
        for input_line in inputs:
            result_line += input_line[(i/j) % len(input_line)]
            j *= len(input_line)
        product.append([result_line])
    return product

def solve(cake: List[List[str]]) -> List[List[str]]:
    letters: str = ''
    unk: List[Tuple[(int, int)]] = []
    for x in range(len(cake)):
        first: List[str] = cake[0]
        for y in range(len(first)):
            if (cake[x][y] == '?'):
                unk.append((x, y))
            else:
                letters += cake[x][y]

    letters_list: List[List[str]] = []
    for i in range(len(unk)):
        letters_list.append([letters])
    attempts: List[List[str]] = cartesian_product(letters_list)

    for attempt in attempts:
        for i in range(len(unk)):
            a: Tuple[(int, int)] = unk[i]
            b: str = attempt[i]
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
    case_number: int = case + 1
    print('Case #' + str(case_number) + ': ')
    result: List[List[str]] = solve(cake)
    for index in range(len(result)):
        print(result[index])
