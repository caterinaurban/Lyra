# RESULT   2:(Integer, OCT( +2.1 - 1.0 >= 0), T), 2.1 * [6:(Integer, T, T), 6.1 * [12:(String, T, (set(), {'G', 'T', 'A', 'C'})), ★], 23:(String, T, (set(), {'.', '#'}))]
import sys
sys.stdin = open('dna_frequency.in', 'r')
number_of_sequences: int = int(input())
if number_of_sequences < 1:
    raise ValueError("Expecting at least one DNA sequence")
for s in range(number_of_sequences):
    sequence_length: int = int(input())
    A_count: int = 0
    C_count: int = 0
    G_count: int = 0
    T_count: int = 0
    for i in range(sequence_length):
        base: str = input()
        if base == 'A':
            A_count: int = A_count + 1
        elif base == 'C':
            C_count: int = C_count + 1
        elif base == 'G':
            G_count: int = G_count + 1
        elif base == 'T':
            T_count: int = T_count + 1
        else:
            raise ValueError
    separator: str = input()
    if separator == '.' or separator == '#':
        pass
    else:
        raise ValueError
    print("Frequency of A nucleotide:")
    print(A_count)
    print("Frequency of C nucleotide:")
    print(C_count)
    print("Frequency of G nucleotide:")
    print(G_count)
    print("Frequency of T nucleotide:")
    print(T_count)