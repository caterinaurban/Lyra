import math
import numpy as np
import itertools


sandmousefile = 'data/sandmouse.fa.txt'
path = '/home/madi/Documents/ETH/master/masterthesis/lyrarep/Lyra/data_quality/examples/homeworks/mcb112/data/'

pathogen = []  # Inititializing an empty list
for line in open(path + "pathogen.fa.txt"):  # For each line in the input file
    line = line.rstrip('\n')  # Remove the trailing newline
    if line[0] != '>': continue  # Skip comment lines
    pathogen.append(line)  # Split into fields on whitespace

sandmouse = []  # Inititializing an empty list
for line in open(sandmousefile):  # For each line in the input file
    line = line.rstrip('\n')  # Remove the trailing newline
    if line[0] == '>': continue  # Skip comment lines
    sandmouse.append(line)  # Split into fields on whitespace

moriartyneg = []  # Inititializing an empty list
for line in open(path + "moriarty-neg.fa.txt"):  # For each line in the input file
    line = line.rstrip('\n')  # Remove the trailing newline
    if line[0] == '>': continue  # Skip comment lines
    moriartyneg.append(line)  # Split into fields on whitespace

# Just checking that we read the fasta files as expected
print("The first two lines extracted from pathogen.fa:\n", pathogen[0:2], "\n")
print("Accessing a the 5th base of the 1st sequence:\n", pathogen[0][4])

# Calculate Moriarty's scores for all datasets
path_mor_score = comp_moriartyscores(pathogen)

path_mor_score = []  # Inititializing an empty list to store all the scores of all sequences
for read in range(len(pathogen)):  # loop through and get the index for each line (or read)
    seqscore = 0  # start with a score of 0 for each read
    for base in range(len(pathogen[read])):  # loop through and get index for each base in the read
        if pathogen[read][base] == "A" or pathogen[read][base] == "T":
            seqscore += 1
        if pathogen[read][base] == "C" or pathogen[read][base] == "G":
            seqscore -= 1  # Add the score based on whether there was an A/T or G/C
    path_mor_score.append(seqscore)

sand_mor_score = []  # Inititializing an empty list to store all the scores of all sequences
for read in range(len(sandmouse)):  # loop through and get the index for each line (or read)
    seqscore = 0  # start with a score of 0 for each read
    for base in range(len(sandmouse[read])):  # loop through and get index for each base in the read
        if sandmouse[read][base] == "A" or sandmouse[read][base] == "T":
            seqscore += 1
        if sandmouse[read][base] == "C" or sandmouse[read][base] == "G":
            seqscore -= 1  # Add the score based on whether there was an A/T or G/C
    sand_mor_score.append(seqscore)

morneg_mor_score = []  # Inititializing an empty list to store all the scores of all sequences
for read in range(len(moriartyneg)):  # loop through and get the index for each line (or read)
    seqscore = 0  # start with a score of 0 for each read
    for base in range(len(moriartyneg[read])):  # loop through and get index for each base in the read
        if moriartyneg[read][base] == "A" or moriartyneg[read][base] == "T":
            seqscore += 1
        if moriartyneg[read][base] == "C" or moriartyneg[read][base] == "G":
            seqscore -= 1  # Add the score based on whether there was an A/T or G/C
    morneg_mor_score.append(seqscore)

# Checking that we do indeed get the scores for all elements as expected
print(pathogen[0:1])  # The first sequence from pathogen dataset
print(path_mor_score[0:10])  # Scores for the first 10 sequences
print(len(pathogen))  # Total number of sequences in pathogen dataset
print(len(path_mor_score))  # Total number of scores for the pathogen dataset

min_score = np.min([path_mor_score, morneg_mor_score])  # Getting the minimum score across both datasets
max_score = np.max([path_mor_score, morneg_mor_score])  # Getting the maximum score across both datasets
thresholds = np.linspace(min_score, max_score, 1000)  # Getting threshold values across the range between min and max scores

len_path = len(path_mor_score)  # Getting number of sequences in pathogen dataset
len_neg = len(morneg_mor_score)  # Number of sequences in random sequence dataset

roc_x = []  # Initializing empty lists to store values for roc plots
roc_y = []

TP = 0  # Setting variables to store true pos, false neg, etc. values
FN = 0
FP = 0
TN = 0

for T in thresholds:  # Iterate through each threshold value
    for i in range(len_path):  # Iterate through pathogen scores and compare to threshold value
        if path_mor_score[i] >= T:  # If pathogen score >= threshold value, it is a true positive
            TP += 1
        if path_mor_score[i] < T:  # If pathogen score < threshold value, it is a false negative
            FN += 1

    for i in range(len_neg):
        if morneg_mor_score[i] >= T:  # If random seq score >= threshold value, it is a false positive
            FP += 1
        if morneg_mor_score[i] < T:  # If random seq score < threshold value, it is a true negative
            TN += 1

    sensitivity = TP / (TP + FN)
    specificity = TN / (TN + FP)
    FPR = 1 - specificity  # FPR = False positive rate

    roc_x.append(FPR)  # Add values to roc plot lists
    roc_y.append(sensitivity)
    TP = 0  # Reset FP, TP, FN, TN values for the next threshold value
    FN = 0
    FP = 0
    TN = 0

min_score2 = np.min([path_mor_score, sand_mor_score])
max_score2 = np.max([path_mor_score, sand_mor_score])

len_sand = len(sand_mor_score)

roc_x2 = []
roc_y2 = []

TP = 0
FN = 0
FP = 0
TN = 0

for T in thresholds:
    for i in range(len_path):
        if path_mor_score[i] >= T:
            TP += 1
        if path_mor_score[i] < T:
            FN += 1

    for i in range(len_sand):
        if sand_mor_score[i] >= T:
            FP += 1
        if sand_mor_score[i] < T:
            TN += 1

    sensitivity2 = TP / (TP + FN)
    specificity2 = TN / (TN + FP)
    FPR2 = 1 - specificity2

    roc_x2.append(FPR2)
    roc_y2.append(sensitivity2)
    TP = 0
    FN = 0
    FP = 0
    TN = 0

path_training = pathogen[0:int(len_path / 2)]  # Selecting half the sequences as pathogen training set
sand_training = sandmouse[0:int(len_sand / 2)]  # Selecting half the sequences as sandmouse training set

path_test = pathogen[int(len_path / 2):int(len_path)]  # Selecting the other half for test sets
sand_test = sandmouse[int(len_sand / 2):int(len_sand)]

seq_1mers = ['A', 'G', 'C', 'T']  # Just a list of all bases as singletons
seq_2mers = [''.join(i) for i in
             itertools.product(seq_1mers, repeat=2)]  # A way to find all twomer combinations from the singletons
seq_3mers = [''.join(i) for i in
             itertools.product(seq_1mers, repeat=3)]  # Threemer combinations from the singletons

seq_1mers_d = dict.fromkeys(seq_1mers, 0)  # Making dictionaries from lists to store scores later on
seq_2mers_d = dict.fromkeys(seq_2mers, 0)
seq_3mers_d = dict.fromkeys(seq_3mers, 0)

print("List of 1mers:\n ", seq_1mers, "\n")  # Checking to see if our lists/dicts look as expected
print("List of 2mers:\n ", seq_2mers, "\n")
print("List of 3mers:\n ", seq_3mers, "\n")
print("Dictionary of 3mers: \n", seq_3mers_d)

# Step 1: Calculate counts per 3mer across all training sequences
seq_3mers_d_path = dict.fromkeys(seq_3mers,
                                 0)  # Making a dictionary to store 3mer frequencies from pathogen training dataset

for i in range(len(path_training)):  # Iterate through the pathogen training sequences
    kmer_count = len(path_training[i]) - 2  # kmer count = number of 3mers per sequence = sequence length-2
    for k in range(kmer_count):  # for each kmer index...
        seq_3mers_d_path[path_training[i][k:k + 3]] += 1  # add 1 to the corresponding key (3mer) in dictionary
# This gives us a count per 3mer in training set

# Step 2: Divide individual 3mer counts by total number of 3mers
# We get P(ATA), P(ATG), P(ATC), P(ATT), etc.

total_kmervals_path = sum(seq_3mers_d_path.values())  # how many total 3mers did we have?
for key, value in seq_3mers_d_path.items():  # for each value in the dictionary, which is currently the 3mer count
    seq_3mers_d_path[
        key] = value / total_kmervals_path  # divide by total 3mers to get the 3mer frequency in training set

# Step 3: Calculate conditional probabilities as follows
# P(A|CG) = P(CGA) / [P(CGA)+P(CGT)+P(CGC)+P(CGG)]

seq_3mers_d_path2 = seq_3mers_d_path.copy()  # Make a copy of the 3mer frequency dictionary
for key, value in seq_3mers_d_path2.items():  # Iterate through the dictionary
    first2 = key[0:2]  # Get the first two bases from each key
    denom = 0  # We will calculate the denominator [P(CGA)+P(CGT)+P(CGC)+P(CGG)]
    for base in seq_1mers:  # Taking one base at a time
        temp = first2 + base  # Concatenating to the first two bases
        denom += seq_3mers_d_path[temp]  # Adding the frequencies of 3mers with the same first two bases
    seq_3mers_d_path2[key] = value / denom  # Storing the conditional probability of each 3mer in copied dictionary

# Step 4: Calculate probabilities of 2mers (P(CG), etc.)
for item in seq_2mers:
    seq_3mers_d_path2[item] = 0
    for base in seq_1mers:
        threemer = item + base
        seq_3mers_d_path2[item] += seq_3mers_d_path[threemer]
print(seq_3mers_d_path2)  # Checking the contents of our dictionary

seq_3mers_d_sand = dict.fromkeys(seq_3mers, 0)

for i in range(len(sand_training)):
    kmer_count = len(sand_training[i]) - 2
    for k in range(kmer_count):
        seq_3mers_d_sand[sand_training[i][k:k + 3]] += 1

total_kmervals_sand = sum(seq_3mers_d_sand.values())
for key, value in seq_3mers_d_sand.items():
    seq_3mers_d_sand[key] = value / total_kmervals_sand

seq_3mers_d_sand2 = seq_3mers_d_sand.copy()
for key, value in seq_3mers_d_sand2.items():
    first2 = key[0:2]
    denom = 0
    for base in seq_1mers:
        temp = first2 + base
        denom += seq_3mers_d_sand[temp]
    seq_3mers_d_sand2[key] = value / denom

# Get probabilities of three-mers and marginalize to get probabilities of two-mers
for item in seq_2mers:
    seq_3mers_d_sand2[item] = 0
    for base in seq_1mers:
        threemer = item + base
        seq_3mers_d_sand2[item] += seq_3mers_d_sand[threemer]
print(seq_3mers_d_sand2)

# Step 5 (described above)
# Calculating pathogen scores
pathtest_scores = []
for i in range(len(path_test)):
    currentscore = 0
    for j in range(len(path_test[0]) - 2):
        currentscore += math.log(
            seq_3mers_d_path2[path_test[i][j:j + 3]] / seq_3mers_d_sand2[path_test[i][j:j + 3]])
    currentscore += math.log(seq_3mers_d_path2[path_test[i][0:2]] / seq_3mers_d_sand2[path_test[i][0:2]])
    pathtest_scores.append(currentscore)

print(pathtest_scores[0:5])

# Calculating sandmouse scores
sandtest_scores = []
for i in range(len(sand_test)):
    currentscore = 0
    for j in range(len(sand_test[0]) - 2):
        currentscore += math.log(
            seq_3mers_d_path2[sand_test[i][j:j + 3]] / seq_3mers_d_sand2[sand_test[i][j:j + 3]])
    currentscore += math.log(seq_3mers_d_path2[sand_test[i][0:2]] / seq_3mers_d_sand2[sand_test[i][0:2]])
    sandtest_scores.append(currentscore)

print(sandtest_scores[0:5])