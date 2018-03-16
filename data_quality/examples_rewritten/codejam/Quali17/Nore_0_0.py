t: int = int(input())

for tc in range(1, t + 1):
    print("Case #")  # print without multiple arguments
    print(tc)
    print(": ")
    line_str: str = input()  # instead of line, k = input().strip().split()
    k_str: str = input()
    k: int = int(k_str)
    line: List[bool] = [False, False, False]  # instead of empty list
    # loop instead of list comprehension
    for i in range(len(line_str)):  # i in range(line_str) instead of c in line_str
        line[i]: bool = line_str[i] == "+"
    r: float = 0
    for i in range(len(line) - k + 1):
        if not line[i]:
            r: float = r + 1  # rewritten +=
            for j in range(k):
                line[i+j]: bool = not line[i+j]
    # loop instead of all(line)
    all_line: bool = True
    for i in range(len(line)):
        if not line:
            all_line: bool = False
    if all_line:
        print(r)
    else:
        print("IMPOSSIBLE")
