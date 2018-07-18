"""
Source: https://github.com/jordancheah/DNA-FASTA-Python/blob/master/dna3.py
Analyzing DNA sequences in Multi-Fasta Format using Python
A Python program that takes as input a file containing DNA sequences in multi-FASTA format, and computes
the answers to the following questions:
* How many records are in the file? A record in a FASTA file is defined as a single-line header, followed
by lines of sequence data. The header line is distinguished from the sequence data by a greater-than (">")
symbol in the first column. The word following the ">" symbol is the identifier of the sequence, and the
rest of the line is an optional description of the entry. There should be no space between the ">" and the
first letter of the identifier.
* What are the lengths of the sequences in the file? What is the longest sequence and what is the shortest
sequence? Is there more than one longest or shortest sequence? What are their identifiers?
"""


# Find ORF in Sequence
def find_orf(sequence):
    # Find all ATG indexs
    start_position = 1
    start_indexs = []
    stop_indexs = []
    for i in range(1, len(sequence), 3):
        if sequence[i:i + 3] == "ATG":
            start_indexs.append(i)

    # Find all stop codon indexs
    for i in range(1, len(sequence), 3):
        stops = ["TAA", "TAA", "TGA"]
        if sequence[i:i + 3] in stops:
            stop_indexs.append(i)

    orf = []
    mark = 0
    for i in range(0, len(start_indexs)):
        for j in range(0, len(stop_indexs)):
            if start_indexs[i] < stop_indexs[j] and start_indexs[i] > mark:
                orf.append(sequence[start_indexs[i]:stop_indexs[j] + 3])
                mark = stop_indexs[j] + 3
                break
    return orf


"""
Question = How many records are in the file?
Answer = 17
"""

f = open("dna3.fasta", "r")
file = f.read()
seqcount = file.count('>')
print("Number of sequence = " + str(seqcount))

"""
Question = What are the lengths of the sequences in the file? 
           What is the longest sequence and what is the shortest sequence?
Answer = Longest is 4773, Shortest is 37
"""

f = open("dna3.fasta", "r")
file = f.readlines()

sequences = []
seq = ""
for f in file:
    if not f.startswith('>'):
        f = f.replace(" ", "")  # remove all spaces and newline from the text
        f = f.replace("\n", "")
        seq = seq + f  # ... then form a long sequence
    else:
        sequences.append(seq)
        seq = ""

sequences.append(seq)
sequences = sequences[1:]  # discard the first sequence, since it is null

lengths = [len(s) for s in sequences]
print("\nMax sequence length = " + str(max(lengths)))
print("Min sequence length = " + str(min(lengths)))

print("\nSequence Length Report:")
for j in range(seqcount):
    print("Length of sequence " + str(j) + " is " + str(lengths[j]))

"""
Queston: what is the length of the longest ORF in the file?
"""

n = 1
lengths = []
for s in sequences:
    orfs = find_orf(s)
    print("ORF")
    for j in orfs:
        print(j)
        print("================")
        lengths.append(len(j))

print("\nLongest ORF is:" + str(max(lengths)))
