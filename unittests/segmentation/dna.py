list_nucl = list(map(int, input().split()))

# Total nucleotides seen so far.
total_count = 0

# Number of G and C nucleotides seen so far.
gc_count = 0

i = 1
while i < len(list_nucl):
    total_count = total_count + 1

    base = list_nucl[i]
    if base == 3 or base == 7: # 3 = 'C', 7 = 'G',
        gc_count = gc_count + 1
    i+=1

gc_content = gc_count / total_count

print(gc_content)
