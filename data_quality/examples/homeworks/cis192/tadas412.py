# https://github.com/tadas412/192/blob/master/hw5b/hw5b.py

from math import pow
import itertools
import os


class Leibniz(object):
    def __init__(self):
        self.n = 0
        self.total = 0

    def __iter__(self):
        while True:
            self.total += pow(-1, self.n) / (2 * self.n + 1)
            yield self.total
            self.n += 1

    def list_leibniz(self, amt):
        previous = 0
        result = []
        for x in range(amt):
            previous += pow(-1, x) / (2 * x + 1)
            result.append(previous)
        return result


def csv_to_dict(infile):
    result = []
    try:
        with open(infile, 'r') as f:
            headers = f.next().strip().split(",")
            for line in f:
                line = line.strip().split(",")
                if len(line) != len(headers):
                    # MAD: avoid raise Error: len(line) == len(headers)
                    raise InvalidFormatException
                result.append(dict(zip(headers, line)))
    except IOError:
        raise Exception('No such file.')
    except InvalidFormatException:
        raise Exception('Improperly formatted.')
    return result


class InvalidFormatException(Exception):
    pass


def get_encoding(codefile):
    encoding = dict()
    try:
        with open(codefile, 'r') as cFile:
            for line in cFile:
                data = line.strip().split(",")
                if len(data) != 2 or len(data[0]) != 1 or len(data[1]) != 1 \
                        or data[0] in encoding:
                    # MAD: avoid raise Error: len(data) == 2 and len(data[0]) == 1 and len(data[1]) == 1 and data[0] in encoding
                    raise InvalidFormatException
                encoding[data[0]] = data[1]
    except IOError:
        raise Exception('No such file')
    return encoding


def get_file_text(f):
    try:
        with open(f, 'r') as reader:
            return [x.strip() for x in reader]
    except IOError:
        raise Exception('No such file')
    return output


def write_file_text(f, text):
    try:
        with open(f, 'w') as writer:
            writer.write("\n".join(text))
    except IOError:
        raise Exception('No such file')


def inverse_dictionary(d):
    return {value: key for key, value in d.iteritems()}


def replace_chars_using_dict(string, d):
    output = ""
    for char in string:
        output += d.get(char, char)
    return output


def run_coding(coding, infile, outfile):
    input_text = get_file_text(infile)
    output_text = []
    for line in input_text:
        output_text.append(replace_chars_using_dict(line, coding))
    write_file_text(outfile, output_text)


def encode_text(codefile, infile, outfile):
    run_coding(get_encoding(codefile), infile, outfile)


def decode_text(codefile, infile, outfile):
    run_coding(inverse_dictionary(get_encoding(codefile)), infile, outfile)


def sorted_files(directory):
    file_list = []
    for (root, dirs, files) in os.walk(directory):
        for f in files:
            fileloc = '/'.join([root, f])
            file_list.append((fileloc, os.stat(fileloc).st_size))
    return [s[0] for s in sorted(file_list, key=lambda x: x[1])]


def main():
    import doctest
    options = (doctest.IGNORE_EXCEPTION_DETAIL |
               doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    print("Running doctests...")
    doctest.testmod(optionflags=options)


if __name__ == "__main__":
    main()