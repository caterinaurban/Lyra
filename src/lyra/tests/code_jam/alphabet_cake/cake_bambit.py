def solve() -> None:
    line: List[str] = sys.stdin.readline().rstrip().split()
    R: int = int(line[0])
    C: int = int(line[1])
    cake_map: Dict[(str, Tuple[(int, int, int, int)])] = {
        
    }
    cake: List[List[str]] = []
    for row_num in range(R):
        row: List[str] = list(sys.stdin.readline().rstrip())
        cake.append(row)
        for (col_num, char) in enumerate(row):
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
            (l, r, u, d) = cake_map[char]
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
        print(''.join(row))

def main() -> None:
    T: int = int(sys.stdin.readline().rstrip())
    for t in range(1, (T + 1)):
        print('Case #{}:'.format(t))
        answer: None = solve()
if (__name__ == '__main__'):
    main()
