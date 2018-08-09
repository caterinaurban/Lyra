
# INITIAL: 3:(Integer, [1, inf], (∅, Σ)), 3.1 * [7:(Integer, [-inf, inf], (∅, Σ)), 7.1 * 13:(String, [-inf, inf], (∅, {'A', 'C', 'G', 'T'})), 24:(String, [-inf, inf], (∅, {'#', '.'}))]
sequences: int = int(input())
if sequences < 1:
    raise ValueError("Expecting at least one DNA sequence")
for s in range(sequences):
    length: int = int(input())
    a: int = 0
    c: int = 0
    g: int = 0
    t: int = 0
    for i in range(length):
        base: str = input()
        if base == 'A':
            a: int = a + 1
        elif base == 'C':
            c: int = c + 1
        elif base == 'G':
            g: int = g + 1
        elif base == 'T':
            t: int = t + 1
        else:
            raise ValueError
    separator: str = input()
    if separator == '.' or separator == '#':
        pass
    else:
        raise ValueError
    print("Frequency of A nucleotide:")
    print(a)
    print("Frequency of C nucleotide:")
    print(c)
    print("Frequency of G nucleotide:")
    print(g)
    print("Frequency of T nucleotide:")
    print(t)
