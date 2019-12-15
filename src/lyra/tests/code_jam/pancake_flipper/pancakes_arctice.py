def flipped(pancakes: List[str]) -> List[str]:
    return [('+' if (pancake == '-') else '-') for pancake in pancakes]

def solve(table: str, size: int) -> Tuple[(str, int)]:
    table_lst: List[str] = list(table)
    moves: int = 0
    for i in range(max(1, (len(table_lst) - size))):
        print(table_lst)
        if (table_lst[i] == '-'):
            table_lst: List[str] = ((table_lst[:i] + flipped(table_lst[i:(i + size)])) + table_lst[(i + size):])
            moves += 1
    for i in range((len(table_lst) - 1), max(((len(table_lst) - size) - 1), (size - 1)), (- 1)):
        print(table_lst)
        if (table_lst[i] == '-'):
            i += 1
            table_lst: List[str] = ((table_lst[:(i - size)] + flipped(table_lst[(i - size):i])) + table_lst[i:])
            moves += 1
    print(table_lst)
    return (''.join(table_lst), moves)
tests: List[Tuple[(str, int)]] = []
for line in open('A-small-attempt1.in', 'r').readlines()[1:]:
    tmp: List[str] = line.split()
    table: str = tmp[0]
    size: str = tmp[1]
    tests += [(table, int(size))]
results: List[str] = []
i: int = 0
for (table, size) in tests:
    print((table + str(size)))
    (final_table, moves) = solve(table, size)
    if ('-' in final_table):
        moves: object = 'IMPOSSIBLE'
    i += 1
    print(f'Case #{i}: {moves}')
    results += [f'Case #{i}: {moves}']
with open('out.txt', 'w') as results_file:
    for result in results:
        results_file.write((result + '\n'))
