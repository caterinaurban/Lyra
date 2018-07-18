# source: http://rosalind.info/problems/cons/

T: int = int(input())
# not given in the original problem
n: int = int(input())

count_a: List[int] = [0] * n
count_c: List[int] = [0] * n
count_g: List[int] = [0] * n
count_t: List[int] = [0] * n

for i in range(T):
    s: str = input()
    if len(s) != n:
        raise ValueError
    # treatng strings as list of characters
    for i in range(n):
        if s[i] == 'A':
            count_a[i]: int = count_a[i] + 1
        elif s[i] == 'C':
            count_c[i]: int = count_c[i] + 1
        elif s[i] == 'G':
            count_g[i]: int = count_g[i] + 1
        elif s[i] == 'T':
            count_t[i]: int = count_t[i] + 1
        else:
            raise ValueError

