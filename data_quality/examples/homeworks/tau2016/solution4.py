
def creates_scores_dict():
    scores_string = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
    scores_dict = {}
    for i ,symbol in enumerate(scores_string):
        scores_dict[symbol] = i + 1
    return scores_dict

scores_dict = creates_scores_dict()
print(scores_dict)


def mean_score(read_quality_string):
    sum = 0
    scores_dict = creates_scores_dict()  # we need to call the dictionary to have it initiated
    for char in read_quality_string:
        sum += scores_dict[char]
    return sum/ len(read_quality_string)


assert (mean_score('!!!!!') == 1.0)
assert (round(mean_score('49@5<*>=E'), 2) == 25.78)


def parse_FASTQ(file):
    with open(file) as f:  # by default, open() uses 'r' argument (read), so we don't have to write it
        quality_dict = {}
        last_line = ""
        line = f.readline()
        while line:
            # here we can use for loop, but usually when iterating over an object - do not change it inside the loop

            line = line.strip()
            # attention! a quality score line can start with '@' - so we have to distinguish between the
            # two types of lines. We know that the quality score line comes after a '+' line

            if line.startswith('@') and last_line != "+":
                # it's a sequence identifier line - so the next one is the sequence
                line = f.readline().strip()
                seq = line

            elif last_line == "+":
                # we reached a quality score line
                quality_dict[seq] = mean_score(line)

            last_line = line
            line = f.readline()
    return quality_dict


# parse lambda reads file
lambda_reads_file = "lambda_reads.fq"
lambda_seqs_dict = parse_FASTQ(lambda_reads_file)

# example
print(lambda_seqs_dict["ATTGAACAAATTAACATCGCTCTGGAGCAAAAAGGGTCCNGGAATTTGTCAGCCTGGGTCA"])
print(mean_score("7CD0D/1G9!9/H'482-E\",G:,6A;:>34-)5;44B&8-$D8260#\".$:>=?%7D\":8"))