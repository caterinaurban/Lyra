import sys


def filename_to_string(dna_filename):
    inputfile = open(dna_filename)

    seq = ""

    linenum = 0

    for line in inputfile:
        linenum = linenum + 1
        if linenum % 4 == 2:
            line = line.rstrip()
            seq = seq + line
    return seq


if len(sys.argv) < 2:
    print("You must supply a file name as an argument when running this program.")
    sys.exit(2)

inputfile = open(sys.argv[1])

nucleotides = ""

linenum = 0

for line in inputfile:
    linenum = linenum + 1
    if linenum % 4 == 2:
        line = line.rstrip()
        nucleotides = nucleotides + line

total_count = 0

gc_count = 0
at_count = 0
g_count = 0
c_count = 0
a_count = 0
t_count = 0

for base in nucleotides:
    total_count = total_count + 1

    if base == 'C':
        gc_count += 1
        c_count += 1
    if base == 'G':
        gc_count += 1
        g_count += 1
    if base == 'A':
        at_count += 1
        a_count += 1
    if base == 'T':
        at_count += 1
        t_count += 1
    if base not in ('C', 'G', 'A', 'T', 'N'):
        print(base)

# MAD: total_count cannot be zero => len(nucleotides) > 0 => inputfile must have >= 2 lines and line != ''
gc_content = float(gc_count) / total_count
at_content = float(at_count) / total_count
g_content = float(g_count) / total_count
c_content = float(c_count) / total_count
a_content = float(a_count) / total_count
t_content = float(t_count) / total_count

print('GC-content:', gc_content)
print('AT-content:', at_content)
print('G count:', g_content)
print('C count:', c_content)
print('A count:', a_content)
print('T count:', t_content)
print('Sum of G+C+A+T counts:', g_content + c_content + a_content + t_content)
print('Total count:', total_count)
print('Length of nucleotides:', len(nucleotides))

# MAD: total_count == len(nucleotides)
assert total_count == len(nucleotides), "total_count != length of nucleotides"
# MAD: g_content + c_content + a_content + t_content == 1
assert g_content + c_content + a_content + t_content == 1, "sum of GCAT incorrect"
