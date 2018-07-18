# source: http://rosalind.info/problems/dna/
T: int = int(input())

for i in range(T):
    count_a: int = 0
    count_c: int = 0
    count_g: int = 0
    count_t: int = 0
    sequence: str = input()
    for j in range(len(sequence)):
        if sequence[j] == 'A':
            count_a: int = count_a + 1
        elif sequence[j] == 'C':
            count_c: int = count_c + 1
        elif sequence[j] == 'G':
            count_g: int = count_g + 1
        elif sequence[j] == 'T':
            count_t: int = count_t + 1
        else:
            raise ValueError
