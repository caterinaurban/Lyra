def update(s: List[str], i: int) -> None:
    if (s[i] == '+'):
        s[i]: str = '-'
    elif (s[i] == '-'):
        s[i]: str = '+'
if (__name__ == '__main__'):
    num: int = int(sys.stdin.readline().strip())
    for case in range(num):
        input_line: str = sys.stdin.readline().strip()
        s: List[str] = [i for i in input_line.split(' ')[0]]
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
            print(('Case #%s: %s' % ((case + 1), move)))
        else:
            print(('Case #%s: IMPOSSIBLE' % (case + 1)))
