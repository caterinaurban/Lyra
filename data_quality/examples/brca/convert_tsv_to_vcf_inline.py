# https://github.com/BRCAChallenge/brca-exchange/blob/master/pipeline/data_merging/convert_tsv_to_vcf.py
#!/usr/bin/env python
"""
this script converts a tsv file into a vcf file
"""
import argparse
import fileinput
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    parser.add_argument("-s", "--source")
    parser.add_argument("-d", "--delimiter", default="\t")
    parser.add_argument("-g", "--version", choices=['37', '38'], default="38",
        help="genome assembly version can be either GRCh37 or GRCh38")
    args = parser.parse_args()
    if args.input is None:
        args.input = 'input.txt'
    if args.output is None:
        args.output = 'output.txt'
    tsv = open(args.input, "r")
    line_num = 0
    info_keys = []
    infos = []
    for line in tsv:
        line_num += 1
        if line_num == 1:
            info_keys = line.strip().split(args.delimiter)
        else:
            info_values = line.strip().split(args.delimiter)
            infos.append(dict(zip(info_keys, info_values)))

    # MAD: info["Genomic_Coordinate"].split(":")[0][3:] must be 13 or 17
    # MAD: each element info in infos:
    # MAD:      info must contain 'Genomic_Coordinate'
    # MAD:      and len(info["Genomic_Coordinate"].split(":")) > 2
    # MAD:      and info["Genomic_Coordinate"] must contain at least two ':'
    # MAD:      and info["Genomic_Coordinate"].split(":")[2] must contain at least one >
    # MAD:      and info["Genomic_Coordinate"].split(":")[1] must be int
    # MAD: info['Genomic_Coordinate] has to be {0} (...13|...17) {1} int {2} .*>.* {3} T {len}? with delimiter ':'
    info_dict = {13:{}, 17:{}}
    # MAD: info_dict must contain info["Genomic_Coordinate"].split(":")[0][3:]
    # MAD: each element info in infos:
    # MAD:      info must contain 'Genomic_Coordinate'
    # MAD:      and len(info["Genomic_Coordinate"].split(":")) > 2
    # MAD:      and info["Genomic_Coordinate"] must contain at least two ':'
    # MAD:      and info["Genomic_Coordinate"].split(":")[2] must contain at least one >
    # MAD:      and info["Genomic_Coordinate"].split(":")[1] must be int
    for info in infos:

        # MAD: info_dict must contain info["Genomic_Coordinate"].split(":")[0][3:]
        # MAD: info must contain 'Genomic_Coordinate'
        # MAD: and len(info["Genomic_Coordinate"].split(":")) > 2
        # MAD: and info["Genomic_Coordinate"] must contain at least two ':'
        # MAD: and info["Genomic_Coordinate"].split(":")[2] must contain at least one >
        # MAD: and info["Genomic_Coordinate"].split(":")[1] must be int
        items = info["Genomic_Coordinate"].split(":")
        # MAD: info_dict must contain items[0][3:] and len(items) > 2 and items[2] must contain at least one >
        chrom = items[0][3:]
        # MAD: items[1] must be int
        pos = items[1]
        ref = items[2].split(">")[0]
        # MAD: len(items) > 2 and items[2] must contain at least one >
        alt = items[2].split(">")[1]

        chrom = int(chrom)
        # MAD: pos must be int
        pos = int(pos)
        # MAD: info_dict must contain chrom
        if pos not in info_dict[chrom]:
            info_dict[chrom][pos] = [info]
        else:
            info_dict[chrom][pos].append(info)
    ordered_dict = []
    for chromosome in sorted(info_dict):
        for position in sorted(info_dict[chromosome]):
            ordered_dict += info_dict[chromosome][position]
    # MAD: each element 'info' in 'ordered_dict':
    # MAD: info must contain 'Genomic_Coordinate'
    # MAD: and info["Genomic_Coordinate"] must contain at least three ':'
    # MAD: and info["Genomic_Coordinate"].split(:)[2] must contain at least one '>'
    sorted_infos = ordered_dict

    f_out = open(args.output + ".header", "w")
    f_out.write("##fileformat=VCFv4.0\n")
    f_out.write("##source={0}\n".format(args.source))
    f_out.write("##reference=GRCh{0}\n".format(args.version))
    for info_key in info_keys:
        f_out.write(
                "##INFO=<ID={0},Number=.,Type=String,Description=\"\">\n".format(info_key))
    f_out.write("\t".join(
        ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO\n"]))
    f_out.close()

    f_out = open(args.output + ".body", "w")
    # MAD: each element 'info' in 'sorted_infos':
    # MAD: info must contain 'Genomic_Coordinate'
    # MAD: and info["Genomic_Coordinate"] must contain at least three ':'
    # MAD: and info["Genomic_Coordinate"].split(:)[2] must contain at least one '>'
    for info in sorted_infos:
        # MAD: info must contain 'Genomic_Coordinate'
        # MAD: and info["Genomic_Coordinate"] must contain at least three ':'
        # MAD: and info["Genomic_Coordinate"].split(:)[2] must contain at least one '>'
        items = info["Genomic_Coordinate"].split(":")
        # MAD: len(items[0]) > 3 and items[2] must contain at least one '>'
        chrom = items[0][3:]
        pos = items[1]
        ref = items[2].split(">")[0]
        # MAD: len(items) > 2 and items[2] must contain at least one '>'
        alt = items[2].split(">")[1]
        INFOs = []
        for key, value in info.items():
            ## ; space : not allowed
            value = value.replace(";",".").replace(":",".").replace(" ","_")
            INFOs.append(key + "=" + value)
        new_line = "\t".join([chrom, pos, ".", ref, alt, ".", ".", ";".join(INFOs)])
        f_out.write(new_line + "\n")
    f_out.close()

    with open(args.output, "w") as file:
        file_list = [args.output + ".header", args.output + ".body"]
        input_lines = fileinput.input(file_list)
        file.writelines(input_lines)
    for each_file in file_list:
        os.remove(each_file)


if __name__ == "__main__":
    main()
