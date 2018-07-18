pathogen = []  # Inititializing an empty list
for line in open(path + "pathogen.fa.txt"):  # For each line in the input file
    line = line.rstrip('\n')  # Remove the trailing newline
    if line[0] != '>': continue  # Skip comment lines
    pathogen.append(line)  # Split into fields on whitespace

path_mor_score = []  # Inititializing an empty list to store all the scores of all sequences
for read in range(len(pathogen)):  # loop through and get the index for each line (or read)
    seqscore = 0  # start with a score of 0 for each read
    for base in range(len(pathogen[read])):  # loop through and get index for each base in the read
        if pathogen[read][base] == "A" or pathogen[read][base] == "T":
            seqscore += 1
        elif pathogen[read][base] == "C" or pathogen[read][base] == "G":
            seqscore -= 1  # Add the score based on whether there was an A/T or G/C
        else:
            raise ValueError
    path_mor_score.append(seqscore)