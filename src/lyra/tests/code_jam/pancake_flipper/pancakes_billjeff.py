def update(s: List[str], i: int) -> None:
    if (s[i] == '+'):
        s[i]: str = '-'
    elif (s[i] == '-'):
        s[i]: str = '+'

num: int = int(input().strip())
for case in range(num):
    input_line: str = input().strip()
    s: List[str] = list()
    split_line: List[str] = input_line.split(' ')
    first_line: str = split_line[0]
    i: str
    for i in first_line:
        s.append(i)
    num: int = int(split_line[1])
    move: int = 0
    for i in range(len(s)):
        if (s[i] == '-'):
            if (i < ((len(s) - num) + 1)):
                for j in range(num):
                    update(s, (i + j))
                move += 1
            else:
                move: int = (- 1)
    if (move != (- 1)):
        print('Case #' + str(case + 1) + ': ' + str(move))
    else:
        print('Case #' + str(case + 1) + ':' + ' IMPOSSIBLE')
