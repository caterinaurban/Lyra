def max(x: int, y: int) -> int:
  if x > y:
      return x
  else:
      return y

def min(x: int, y: int) -> int:
  if x < y:
      return x
  else:
      return y


def solve() -> None:
    line: List[str] = input().rstrip().split()
    R: int = int(line[0])
    C: int = int(line[1])
    cake_map0: Dict[str, int] = {}
    cake_map1: Dict[str, int] = {}
    cake_map2: Dict[str, int] = {}
    cake_map3: Dict[str, int] = {}
    cake: List[List[str]] = []
    for row_num in range(R):
        row: List[str] = list(input().rstrip())
        cake.append(row)
        for col_num in range(len(row)):
            char: str = row[col_num]
            if (char == '?'):
                continue
            if (char not in cake_map0):
                cake_map0[char] = col_num
                cake_map1[char] = col_num
                cake_map2[char] = row_num
                cake_map3[char] = row_num
            cake_char0: int = cake_map0[char]
            cake_char1: int = cake_map1[char]
            cake_char2: int = cake_map2[char]
            cake_char3: int = cake_map3[char]
            best_left: int = min(col_num, cake_char0)
            best_right: int = max(col_num, cake_char1)
            best_down: int = max(row_num, cake_char3)
            cake_map0[char] = best_left
            cake_map1[char] = best_right
            cake_map2[char] = cake_char2
            cake_map3[char] = best_down
    for char in cake_map0:
        vals0: int = cake_map0[char]
        vals1: int = cake_map1[char]
        vals2: int = cake_map2[char]
        vals3: int = cake_map3[char]
        for row_num in range(vals2, (vals3 + 1)):
            for col_num in range(vals0, (vals1 + 1)):
                cake[row_num][col_num]: str = char
    while True:
        did_fill: bool = False
        for char in cake_map0:
            cake_map_char0: int = cake_map0[char]
            cake_map_char1: int = cake_map1[char]
            cake_map_char2: int = cake_map2[char]
            cake_map_char3: int = cake_map3[char]
            l: int = cake_map_char0
            r: int = cake_map_char1
            u: int = cake_map_char2
            d: int = cake_map_char3
            if (u > 0):
                for col in range(l, (r + 1)):
                    if (cake[(u - 1)][col] != '?'):
                        break
                else:
                    for col in range(l, (r + 1)):
                        cake[(u - 1)][col]: str = char
                    did_fill: bool = True
                    cake_map0[char] = l
                    cake_map1[char] = r
                    cake_map2[char] = u - 1
                    cake_map3[char] = d
                    l = cake_map0[char]
                    r = cake_map1[char]
                    u = cake_map2[char]
                    d = cake_map3[char]
            if (d < (R - 1)):
                for col in range(l, (r + 1)):
                    if (cake[(d + 1)][col] != '?'):
                        break
                else:
                    for col in range(l, (r + 1)):
                        cake[(d + 1)][col]: str = char
                    did_fill: bool = True
                    cake_map0[char] = l
                    cake_map1[char] = r
                    cake_map2[char] = u
                    cake_map3[char] = d + 1
                    l = cake_map0[char]
                    r = cake_map1[char]
                    u = cake_map2[char]
                    d = cake_map3[char]
            if (l > 0):
                for row in range(u, (d + 1)):
                    if (cake[row][(l - 1)] != '?'):
                        break
                else:
                    for row in range(u, (d + 1)):
                        cake[row][(l - 1)]: str = char
                    did_fill: bool = True
                    cake_map0[char] = l - 1
                    cake_map1[char] = r
                    cake_map2[char] = u
                    cake_map3[char] = d
                    l = cake_map0[char]
                    r = cake_map1[char]
                    u = cake_map2[char]
                    d = cake_map3[char]
            if (r < (C - 1)):
                for row in range(u, (d + 1)):
                    if (cake[row][(r + 1)] != '?'):
                        break
                else:
                    for row in range(u, (d + 1)):
                        cake[row][(r + 1)]: str = char
                    did_fill: bool = True
                    cake_map0[char] = l
                    cake_map1[char] = r + 1
                    cake_map2[char] = u
                    cake_map3[char] = d
                    l = cake_map0[char]
                    r = cake_map1[char]
                    u = cake_map2[char]
                    d = cake_map3[char]
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
