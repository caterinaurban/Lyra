T: int = int(input())
for i in range(T):
    s1: str = input()
    s2: str = input()
    max_length: int = int(input())
    if len(s1) + len(s2) > max_length + 1:
        raise ValueError
    else:
        print(s1, s2)