#!/usr/bin/env python
"""
this script converts a tsv file into a vcf file
"""
import argparse
import fileinput
import os


def main():
    args = arg_parse()
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

    sorted_infos = sort_by_pos(infos)
    write_header(args.output, info_keys, args.source, args.version)
    write_body(args.output, sorted_infos)
    merge_header_body(args.output)


def sort_by_pos(infos):
    info_dict = {13:{}, 17:{}}
    for info in infos:
        [chrom, pos, ref, alt] = parse_genome_coor(info["Genomic_Coordinate"])
        chrom = int(chrom)
        pos = int(pos)
        if pos not in info_dict[chrom]:
            info_dict[chrom][pos] = [info]
        else:
            info_dict[chrom][pos].append(info)
    ordered_dict = []
    for chromosome in sorted(info_dict):
        for position in sorted(info_dict[chromosome]):
            ordered_dict += info_dict[chromosome][position]
    return ordered_dict


def merge_header_body(output_name):
    with open(output_name, "w") as file:
        file_list = [output_name + ".header", output_name + ".body"]
        input_lines = fileinput.input(file_list)
        file.writelines(input_lines)
    for each_file in file_list:
        os.remove(each_file)


def write_header(output_path, info_keys, source, version):
    f_out = open(output_path + ".header", "w")
    f_out.write("##fileformat=VCFv4.0\n")
    f_out.write("##source={0}\n".format(source))
    f_out.write("##reference=GRCh{0}\n".format(version))
    for info_key in info_keys:
        f_out.write(
                "##INFO=<ID={0},Number=.,Type=String,Description=\"\">\n".format(info_key))
    f_out.write("\t".join(
        ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO\n"]))
    f_out.close()


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    parser.add_argument("-s", "--source")
    parser.add_argument("-d", "--delimiter", default="\t")
    parser.add_argument("-g", "--version", choices=['37', '38'], default="38",
        help="genome assembly version can be either GRCh37 or GRCh38")
    return parser.parse_args()


def write_body(path_output, infos):
    f_out = open(path_output + ".body", "w")
    for info in infos:
        [chrom, pos, ref, alt] = parse_genome_coor(info["Genomic_Coordinate"])
        INFOs = []
        for key, value in info.iteritems():
            ## ; space : not allowed
            value = value.replace(";",".").replace(":",".").replace(" ","_")
            INFOs.append(key + "=" + value)
        new_line = "\t".join([chrom, pos, ".", ref, alt, ".", ".", ";".join(INFOs)])
        f_out.write(new_line + "\n")
    f_out.close()

def parse_genome_coor(s):
    items = s.split(":")
    chrom = items[0][3:]
    pos = items[1]
    ref = items[2].split(">")[0]
    alt = items[2].split(">")[1]
    return [chrom, pos, ref, alt]



if __name__ == "__main__":
    main()
