N: int = int(input())
A_count: int = 0
C_count: int = 0
G_count: int = 0
T_count: int = 0
for i in range(N):
    base: str = input()
    if base == 'A':
        A_count: int = A_count + 1
    elif base == 'C':
        C_count: int = C_count + 1
    elif base == 'G':
        G_count: int = G_count + 1
    elif base == 'T':
        T_count: int = T_count + 1
