def max(x: int, y: int):
  if x > y:
      return x
  else:
      return y

def min(x: int, y: int):
  if x < y:
      return x
  else:
      return y


def solve() -> None:
    line: List[str] = input().rstrip().split()
    R: int = int(line[0])
    C: int = int(line[1])
    cake_map: Dict[(str, Tuple[(int, int, int, int)])] = {

    }
    cake: List[List[str]] = []
    for row_num in range(R):
        row: List[str] = list(input().rstrip())
        cake.append(row)
        for col_num in range(len(row)):
            char: str = row[col_num]
            if (char == '?'):
                continue
            if (char not in cake_map):
                cake_map[char]: Tuple[(int, int, int, int)] = (col_num, col_num, row_num, row_num)
            cake_char: Tuple[(int, int, int, int)] = cake_map.get(char)
            best_left: int = min(col_num, cake_char[0])
            best_right: int = max(col_num, cake_char[1])
            best_down: int = max(row_num, cake_char[3])
            cake_map[char]: Tuple[(int, int, int, int)] = (best_left, best_right, cake_char[2], best_down)
    for char in cake_map:
        vals: Tuple[(int, int, int, int)] = cake_map[char]
        for row_num in range(vals[2], (vals[3] + 1)):
            for col_num in range(vals[0], (vals[1] + 1)):
                cake[row_num][col_num]: str = char
    while True:
        did_fill: bool = False
        for char in cake_map:
            cake_map_char: Tuple[(int, int, int, int)] = cake_map[char]
            l: int = cake_map_char[0]
            r: int = cake_map_char[1]
            u: int = cake_map_char[2]
            d: int = cake_map_char[3]
            if (u > 0):
                for col in range(l, (r + 1)):
                    if (cake[(u - 1)][col] != '?'):
                        break
                else:
                    for col in range(l, (r + 1)):
                        cake[(u - 1)][col]: str = char
                    did_fill: bool = True
                    cake_map[char]: Tuple[(int, int, int, int)] = (l, r, (u - 1), d)
                    (l, r, u, d) = cake_map[char]
            if (d < (R - 1)):
                for col in range(l, (r + 1)):
                    if (cake[(d + 1)][col] != '?'):
                        break
                else:
                    for col in range(l, (r + 1)):
                        cake[(d + 1)][col]: str = char
                    did_fill: bool = True
                    cake_map[char]: Tuple[(int, int, int, int)] = (l, r, u, (d + 1))
                    (l, r, u, d) = cake_map[char]
            if (l > 0):
                for row in range(u, (d + 1)):
                    if (cake[row][(l - 1)] != '?'):
                        break
                else:
                    for row in range(u, (d + 1)):
                        cake[row][(l - 1)]: str = char
                    did_fill: bool = True
                    cake_map[char]: Tuple[(int, int, int, int)] = ((l - 1), r, u, d)
                    (l, r, u, d) = cake_map[char]
            if (r < (C - 1)):
                for row in range(u, (d + 1)):
                    if (cake[row][(r + 1)] != '?'):
                        break
                else:
                    for row in range(u, (d + 1)):
                        cake[row][(r + 1)]: str = char
                    did_fill: bool = True
                    cake_map[char]: Tuple[(int, int, int, int)] = (l, (r + 1), u, d)
                    (l, r, u, d) = cake_map[char]
        if (not did_fill):
            break
    for row in cake:
        row_str: str = ''
        for index in range(len(row)):
            row_str += row[index]
        print(row_str)


T: int = int(input().rstrip())
for t in range(1, (T + 1)):
    print('Case #' + str(t) + ':')
    solve()
