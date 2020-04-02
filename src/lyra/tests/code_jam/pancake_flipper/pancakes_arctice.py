def max(x: int, y: int) -> int:
  if x > y:
      return x
  else:
      return y

def flipped(pancakes: List[str]) -> List[str]:
    flipped_pancakes: List[str] = list()
    for pancake in pancakes:
        if pancake == '-':
            flipped_pancakes.append('+')
        else:
            flipped_pancakes.append('-')
    return flipped_pancakes

def solve(table: str, size: int) -> Tuple[(str, int)]:
    table_lst: List[str] = list(table)
    moves: int = 0
    first_range: int = max(1, (len(table_lst) - size))
    for i in range(first_range):
        print(table_lst)
        if (table_lst[i] == '-'):
            table_lst: List[str] = ((table_lst[:i] + flipped(table_lst[i:(i + size)])) + table_lst[(i + size):])
            moves += 1
    second_range: int = max(((len(table_lst) - size) - 1), (size - 1))
    for i in range((len(table_lst) - 1), second_range, (- 1)):
        print(table_lst)
        if (table_lst[i] == '-'):
            i += 1
            table_lst: List[str] = ((table_lst[:(i - size)] + flipped(table_lst[(i - size):i])) + table_lst[i:])
            moves += 1
    print(table_lst)
    table_lst_str: str = ''
    for index in range(len(table_lst)):
        table_lst_str += table_lst[index]
    return (table_lst_str, moves)

tests: List[Tuple[(str, int)]] = []
N: int = int(input())
for i in range(N):
    line: str = input()
    tmp: List[str] = line.split()
    table: str = tmp[0]
    size: str = tmp[1]
    tests += [(table, int(size))]
results: List[str] = []
i: int = 0
for (table, size) in tests:
    print((table + str(size)))
    a_result: Tuple[(str, int)] = solve(table, size)
    final_table: str = a_result[0]
    moves: str = str(a_result[1])
    if ('-' in final_table):
        moves = 'IMPOSSIBLE'
    i += 1
    print('Case #' + str(i) + ':' + moves)
    results += ['Case #' + str(i) + ':' + moves]
for result in results:
    print(result)
