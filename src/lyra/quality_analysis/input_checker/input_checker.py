from math import inf

from lyra.abstract_domains.quality.assumption_lattice import TypeLattice


class InputChecker:
    """
    Checks an input file for errors using a JSON file created by a previously run
    assumption analysis
    """

    def write_type_error(self, error_file, line_num, input_line, type_name):
        if input_line == '':
            error = f'Missing value in line {line_num+1}: ' \
                    f'expected one value of type {type_name}.'
        else:
            error = f'Type Error in line {line_num+1}: ' \
                    f'expected one value of type {type_name} ' \
                    f'instead found \'{input_line}\'.'
        error_file.write(error)
        error_file.write('\n')

    def write_range_error(self, error_file, line_num, input_line, lower, upper):
        error = f'Range Error in line {line_num+1}: ' \
                f'expected one value in range [{lower}, {upper}] ' \
                f'instead found \'{input_line}\'.'
        error_file.write(error)
        error_file.write('\n')

    def check_input(self, filename, assumptions, program_name):
        error_file = open(f'errors_{program_name}.txt', 'w')
        input_file = open(f'../tests/quality/{filename}', 'r')
        line_num = 0
        for assumption in assumptions:
            line_num += 1
            input_line = input_file.readline().strip()
            type_assmp = assumption.type_assumption
            if type_assmp == TypeLattice().integer():
                try:
                    val = int(input_line)
                except ValueError:
                    self.write_type_error(error_file, line_num, input_line, 'integer')
                    continue
            if type_assmp == TypeLattice().real():
                try:
                    val = float(input_line)
                except ValueError:
                    self.write_type_error(error_file, line_num, input_line, 'float')
                    continue

            range_assmp = assumption.range_assumption
            if val < range_assmp.lower or val > range_assmp.upper:
                lower = range_assmp.lower
                upper = range_assmp.upper
                self.write_range_error(error_file, line_num, input_line, lower, upper)
        error_file.close()
        input_file.close()