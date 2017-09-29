# http://courses.cs.tau.ac.il/pyProg/1516b/index.html


def get_x_freqs(infile, outfile, x):
    f = open(infile, 'r')
    words = {}
    for line in f:
        line_lst = line.rstrip().split()
        for word in line_lst:
            words[word] = words.get(word,0) + 1
    f.close()
    
    counts = {}
    for word in words:
        count = words[word]
        curr_list = []
        if count in counts:
            curr_list = counts[count]
        curr_list.append(word)
        counts[count] = curr_list
    
    i = 0
    f2 = open(outfile, 'w')    
    while i < x:
        # MAD: counts cannot be empty if i < x => counts cannot be empty if 0 < x
        # MAD: => if 0 < x then len(words) > 0
        val = max(counts.keys())
        word = counts[val].pop()
        if counts[val] == []:
            counts.pop(val)
        f2.write(word+"\n")        
        i+=1
    f2.close()


def get_pair_location(my_pair, filename):
    f = open(filename, 'r')
    lines = f.readlines()

    pairs = {}
    for i in range(len(lines)):
         lines[i] = lines[i].rstrip()
         words = lines[i].split()
         for j in range(len(words)-1):
             pairs[(words[j], words[j+1])] = i

    for i in range(len(lines)-1):
        words1 = lines[i].split()
        words2 = lines[i+1].split()
        # MAD: len(words1) >= 1 and len(words2) >= 1
        tup = (words1[-1], words2[0])
        if tup in pairs:
            # MAD: max() with same argument types: pairs[tup] must be an int
            pairs[tup] = max(i, pairs[tup])
        else:
            pairs[tup] = i
    
    val =  pairs.get(my_pair, None)
    if val != None: 
        return val + 1
    else:
        return None


def get_csv_matrix(filename):
    f = open(filename, 'r')
    rows = []
    line_num = 0
    row_len = 0 
    for line in f:
        vals = line.split(',')
        row = []
        try:
            for v in vals:
                # MAD: values in line must exist as commaseparated floats (to avoid raise Error (A)
                v = float(v)
                row.append(v)
            rows.append(row)
        except ValueError:
            return None
        if line_num == 0:
            row_len = len(row)
        else: 
            line_num += 1
            # MAD: avoid raise Error (A): if len(f) > 0 and line_num != 0 then len(row) == row_len
            if len(row) != row_len:
                return None
    return rows  # MAD: avoid raise Error (A): len(rows) > 0


def add_csv_mats(file1, file2, outfile):
    
    mat1 = get_csv_matrix(file1)
    mat2 = get_csv_matrix(file2)
    if not mat1 or not mat2:
        # MAD: avoid raise Error (A)
        raise ValueError("Invalid input matrix")

    if len(mat1) != len(mat2):
        # MAD: avoid raise Error: len(mat1) == len(mat2)
        raise ValueError("Row dimensions don't match!")
    elif not all([len(mat1[i]) == len(mat1[0]) and len(mat2[i]) == len(mat1[0]) for i in range(len(mat1))]):
        # MAD: avoid raise Error
        raise ValueError("Column dimensions don't match")

    rows = []
    for i in range(len(mat1)):
        row = []
        for j in range(len(mat1[i])):
            row.append(mat1[i][j] + mat2[i][j])
        rows.append(row)

    f = open(outfile, 'w')
    for row in rows:
        row_str = ','.join([str(val) for val in row])
        f.write(row_str + '\n')
    f.close()

get_x_freqs("marie.txt", "marie.out.txt", 3)
print(get_pair_location(("she", "stopped"), "marie.txt"))
print(get_csv_matrix('good3.csv'))
add_csv_mats("good1.csv", "good2.csv", "mat.out.csv")