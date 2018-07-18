# https://cambridgespark.com/content/tutorials/genetic-ancestry-analysis-python/index.html

row = ['1', '742429', 'rs3094315', 'G', 'A', '.', 'PASS', 'AA=g;AC=46;AN=118;DP=237;HM2;GP=1:752566;BN=103', 'GT:DP:CB', '0|1:3:SM', '1|1:4:MB', '1|0:5:SMB', '0|1:2:SMB', '1|0:6:SMB', '1|0:7:SMB', '0|1:4:SMB', '0|0:4:SMB', '1|1:0:SMB', '1|1:12:SMB', '0|1:4:SMB', '0|1:2:SMB', '1|0:4:MB', '0|0:7:SMB', '1|1:4:SMB', '0|0:4:SMB', '1|1:6:SMB', '0|0:5:SMB', '0|1:4:SMB', '1|1:5:MB', '0|0:6:SMB', '0|0:5:SMB', '0|1:1:SMB', '1|1:2:SMB', '0|0:9:SMB', '0|0:1:SMB', '0|0:10:SMB', '0|1:9:SMB', '1|0:9:SMB', '0|1:2:SMB', '0|1:8:SMB', '1|1:4:SMB', '0|1:9:SMB', '0|0:2:SMB', '1|0:5:SMB', '0|1:2:SMB', '0|0:3:SMB', '0|0:0:SMB', '0|0:4:SMB', '0|1:7:SMB', '1|0:3:SM', '0|0:2:SMB', '0|0:0:SMB', '0|1:9:SMB', '0|1:4:SMB', '0|0:1:SMB', '0|0:1:SMB', '0|0:1:SMB', '0|0:3:SMB', '1|1:2:SMB', '0|0:2:SMB', '1|0:4:SMB', '0|0:2:SMB', '0|0:2:SMB', '1|0:2:SMB', '0|0:0:SMB', '1|0:2:SMB', '1|1:3:SMB', '1|0:4:SMB']



def convert_genotype(row, genotype):
    ref = row[3]
    alt = row[4]

    #assumption: genotype is only GG, AG, GA, AA, with caputal letters, not separated and/or special characters 
    if genotype == ref+ref:
        print("0|0")
    elif (genotype == ref+alt) | (genotype == alt+ref):
        print("0|1")
    elif genotype == alt+alt:
        print("1|1")
    else: # missing genotype, or incorrect annotation, we assume ref/ref
        print("0|0")


def extract_genotype(row):
    genotype = row[9:]
    genotype = [i.split(":")[0] for i in genotype]


row = input()
genotype = row[9:]
new_genotype = []
for g in genotype:
    x = g.split(":")
    x = x[0]
    new_genotype.append(x)
genotype = new_genotype