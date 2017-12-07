from math import inf

from lyra.abstract_domains.quality.assumption_lattice import TypeLattice


class InputChecker:
    """
    Checks an input file for errors using a JSON file created by a previously run
    assumption analysis
    """

    def __init__(self, program_name):
        self._error_file = open(f"errors_{program_name}.txt", 'w')

    def write_missing_error(self, line_num, type_assmp):
        error = f'Missing value in line {line_num}: ' \
                f'expected one value of type {self.type_to_type_name(type_assmp)}.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def write_type_error(self, line_num, input_line, type_assmp):
        error = f'Type Error in line {line_num}: ' \
                f'expected one value of type {self.type_to_type_name(type_assmp)} ' \
                f'instead found \'{input_line}\'.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def write_range_error(self, line_num, input_line, lower, upper):
        error = f'Range Error in line {line_num}: ' \
                f'expected one value in range [{lower}, {upper}] ' \
                f'instead found \'{input_line}\'.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def write_no_error(self):
        error = f'The input data did not violate any assumptions found by the analyzer.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def type_to_type_name(self, type_assmp):
            if type_assmp == TypeLattice().integer():
                return "integer"
            if type_assmp == TypeLattice().real():
                return "float"
            if type_assmp == TypeLattice().top():
                return "string"

    def check_input(self, filename, assumptions):
        input_file = open(f"../tests/quality/{filename}", 'r')
        line_num = 0
        has_errors = False
        for assumption in assumptions:
            line_num += 1
            input_line = input_file.readline().strip()
            type_assmp = assumption.type_assumption
            if input_line == "":
                self.write_missing_error(line_num, type_assmp)
                has_errors = True
                continue
            if type_assmp == TypeLattice().integer():
                try:
                    val = int(input_line)
                except ValueError:
                    self.write_type_error(line_num, input_line, type_assmp)
                    has_errors = True
                    continue
            if type_assmp == TypeLattice().real():
                try:
                    val = float(input_line)
                except ValueError:
                    self.write_type_error(line_num, input_line, type_assmp)
                    has_errors = True
                    continue
            range_assmp = assumption.range_assumption
            if val < range_assmp.lower or val > range_assmp.upper:
                lower = range_assmp.lower
                upper = range_assmp.upper
                self.write_range_error(line_num, input_line, lower, upper)
        if not has_errors:
            self.write_no_error()
        self._error_file.close()
        input_file.close()