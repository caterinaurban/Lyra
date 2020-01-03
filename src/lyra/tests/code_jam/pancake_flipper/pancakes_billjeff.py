def update(s: List[str], i: int) -> None:
    if (s[i] == '+'):
        s[i]: str = '-'
    elif (s[i] == '-'):
        s[i]: str = '+'

num: int = int(input().strip())
for case in range(num):
    input_line: str = input().strip()
    s: List[str] = list()
    for i in input_line.split(' ')[0]:
        s.append(i)
    num: int = int(input_line.split(' ')[1])
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
