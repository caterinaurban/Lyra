dna_list: List[str] = input().split(',')
n = len(dna_list[0])
A = [0]*n
T = [0]*n
G = [0]*n
C = [0]*n
for dna in dna_list:
    for index, base in enumerate(dna):
        if base == 'A':
            A[index] += 1
        elif base == 'C':
            C[index] += 1
        elif base == 'G':
            G[index] += 1
        elif base == 'T':
            T[index] += 1
print(A, C, G, T)