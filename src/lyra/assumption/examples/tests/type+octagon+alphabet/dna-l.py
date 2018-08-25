number_of_sequences: int = int(input())
max_length: int = int(input())
if number_of_sequences <= 0 :
    raise ValueError("Expecting at least one DNA sequence")
for s in range(number_of_sequences):
    sequence_length: int = int(input())
    if sequence_length > max_length:
        raise ValueError
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

# 1:(Integer, >0, OCT(1.1 - 1.0 >= 0), (∅, Σ)), 2:(Integer, ⊤, OCT(1.1 - 1.0 >= 0), (∅, Σ)),
# 1.1 * [6:(Integer, ⊤, OCT(2.1 >= 6.1), (∅, Σ)), 6.1 * 14:(String, ⊤, T, (∅, {'A', 'C', 'G',
# 'T'})), 25:(String, ⊤, T, (∅, {'#', '.'}))]