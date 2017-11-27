# https://nbviewer.jupyter.org/url/mcb112.org/w04/w04-answers-NN.ipynb

import math
import matplotlib.pyplot as plt


def readfasta(datafile):
    data = []
    for line in open(datafile):  # For each line in the input file...
        line = line.rstrip('\n')  # Remove the trailing newline
        if line[0] == '>': continue  # Skip comment lines
        data.append(line)  # Split into fields on whitespace
    return data


# Loop through each sequence and count the number of times each appears:
def train(trainset, nuclist, twomers):
    kmerdict = {}
    # Get all 64 possible k-mers
    for nuc in nuclist:
        for nuc2 in nuclist:
            for nuc3 in nuclist:
                fun = nuc + nuc2 + nuc3
                kmerdict[fun] = 0
    # Get frequency of all k-mers in training set.
    total = 0
    for i in range(len(trainset)):
        for j in range(len(trainset[0]) - 2):
            kmerdict[trainset[i][j:j + 3]] += 1
            total += 1
    # Normalize kmerdict to get probabilities for three-mers
    for elem in kmerdict.keys():
        kmerdict[elem] = kmerdict[elem] / total
    # Get relevant conditonal probabilities. Ex. P(A|CG)=freq(CGA)/(freq(CGA)+freq(CGT)+freq(CGC)+freq(CGG))
    # make a new dictionary copy to store conditional probabilities.
    kmerdict2 = kmerdict.copy()
    for elem in kmerdict.keys():
        elemfirst2 = elem[0:2]
        current = 0
        # Divide by P(two-mer) background to get conditional probability. P(two-mer) is attained by marginalization.
        for nuc in nuclist:
            temp = elemfirst2 + nuc
            current += kmerdict[temp]
        kmerdict2[elem] = kmerdict[elem] / current
    # Get probabilities of three-mers and marginalize to get probabilities of two-mers
    for elem in twomers:
        kmerdict2[elem] = 0
        for nuc in nuclist:
            threemer = elem + nuc
            kmerdict2[elem] += kmerdict[threemer]
    return kmerdict2


def test(traindictpath, traindictsand, testdata):
    scores = []
    for i in range(len(testdata)):
        currentscore = 0
        # Go through all threemers
        for j in range(len(testdata[0]) - 2):
            currentscore += math.log(traindictpath[testdata[i][j:j + 3]] / traindictsand[testdata[i][j:j + 3]])
        # Add first twomer
        currentscore += math.log(traindictpath[testdata[i][0:2]] / traindictsand[testdata[i][0:2]])
        scores.append(currentscore)
    return scores


def main(sandmousedata):
    path = '/home/madi/Documents/ETH/master/masterthesis/lyrarep/Lyra/data_quality/examples/homeworks/mcb112/data/'
    pathogendata = path + "pathogen.fa.txt"
    moriartyneg = "moriarty-neg.fa.txt"
    # sandmousedata = "sandmouse.fa.txt"

    temp = readfasta(pathogendata)
    pathogendata_train = temp[0:int(len(temp) / 2)]
    pathogendata_test = temp[int(len(temp) / 2):len(temp)]
    temp = readfasta(sandmousedata)
    sandmousedata_train = temp[0:int(len(temp) / 2)]
    sandmousedata_test = temp[int(len(temp) / 2):len(temp)]

    nuclist = ['A', 'G', 'C', 'T']
    twomers = ['AA', 'AG', 'AC', 'AT', 'GA', 'GG', 'GC', 'GT', 'CA', 'CG', 'CC', 'CT', 'TA', 'TG', 'TC', 'TT']

    pathogentraindict = train(pathogendata_train, nuclist, twomers)
    sandmousetraindict = train(sandmousedata_train, nuclist, twomers)

    pathscores_me = test(pathogentraindict, sandmousetraindict, pathogendata_test)

    sandscores_me = test(pathogentraindict, sandmousetraindict, sandmousedata_test)

    plt.hist(pathscores_me, alpha=0.5, bins=30, label='pathogen')
    plt.hist(sandscores_me, bins=30, alpha=0.5, label='sandmouse')
    plt.ylabel('Frequency')
    plt.xlabel('Score')
    plt.title('Score Histograms of Pathogen and Sandmouse')
    plt.legend(loc='upper right')
    #plt.show()
