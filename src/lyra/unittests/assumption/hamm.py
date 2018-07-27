
# INITIAL:  3:(String, [-inf, inf]), 4:(String, [-inf, inf]), len(seq1) * []
seq1: str = input()
seq2: str = input()
hamm: int = 0

if len(seq1) != len(seq2):
    raise ValueError

for i in range(len(seq1)):
    if seq1[i] != seq2[i]:
        hamm: int = hamm + 1

print(hamm)
