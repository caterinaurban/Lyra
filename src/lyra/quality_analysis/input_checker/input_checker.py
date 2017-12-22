from math import inf

from lyra.abstract_domains.quality.assumption_lattice import TypeLattice, AssumptionLattice, \
    InputAssumptionLattice


class InputChecker:
    """
    Checks an input file for errors using a JSON file created by a previously run
    assumption analysis
    """

    def __init__(self, program_name):
        self._error_file = open(f"errors_{program_name}.txt", 'w')
        self.input_file = open(f"../tests/quality/{program_name}.in", 'r')


    def write_missing_error(self, num_values_expected, num_values_found):
        """Prints an error because there are more assumptions than values

        :param num_values_expected: number of values that are exptected
        :param num_values_found: number of values that were found in input file
        """
        error = f'Missing value: ' \
                f'expected at least {num_values_expected} values instead found {num_values_found}.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def write_type_error(self, line_num, input_line, type_assmp):
        """Prints an error because an input is not of an expected type

        :param line_num: line number of the input
        :param input_line: input that contains the error
        :param type_assmp: expected type
        """
        error = f'Type Error in line {line_num}: ' \
                f'expected one value of type {self.type_to_type_name(type_assmp)} ' \
                f'instead found \'{input_line}\'.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def write_range_error(self, line_num, input_line, lower, upper):
        """Prints an error because an input is not in an expected range

        :param line_num: line number of the input
        :param input_line: input that contains the error
        :param lower: expected lower bound
        :param upper: exptected upper bound
        """
        error = f'Range Error in line {line_num}: ' \
                f'expected one value in range [{lower}, {upper}] ' \
                f'instead found \'{input_line}\'.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def write_no_error(self):
        """Prints a message that no error has been found
        """
        error = f'The input data did not violate any assumptions found by the analyzer.'
        self._error_file.write(error)
        self._error_file.write('\n')

    def type_to_type_name(self, type_assmp: TypeLattice):
        """Returns the name of the type, given an element of the TypeLattice

        :param type_assmp:
        :return:
        """
        if type_assmp == TypeLattice().integer():
            return "integer"
        if type_assmp == TypeLattice().real():
            return "float"
        if type_assmp == TypeLattice().top():
            return "string"

    def count_values(self, filename: str):
        """Count the number of lines in a file

        :param filename: name of the input file
        :return: number of lines found
        """
        input_file = open(f"../tests/quality/{filename}.in", 'r')
        num = 0
        for _ in input_file:
            num += 1
        input_file.close()
        return num

    def find_num_total_assmps(self, assumptions, curr_iterations):
        """Finds the number of total assumptions

        :param assumptions: assumptions to count
        :param curr_iterations: number of iterations of the current assumptions
        :return: number of assumptions
        """
        num_assmps = 0
        for assmp in assumptions:
            if isinstance(assmp, InputAssumptionLattice):
                num_assmps += self.find_num_total_assmps(assmp.assmps, assmp.iterations)
            else:
                num_assmps += 1
        return curr_iterations * num_assmps

    def check_input(self, filename: str, assumptions: []):
        """Checks if the input file fulfils all the assumptions

        :param filename: filename of the input file
        :param assumptions: all assumptions
        """
        num_values = self.count_values(filename)
        num_total_assmps = self.find_num_total_assmps(assumptions, 1)
        if num_values < num_total_assmps:
            self.write_missing_error(num_total_assmps, num_values)
        has_errors = self.check_assmps(assumptions, 1, 0)
        if not has_errors:
            self.write_no_error()
        self._error_file.close()
        self.input_file.close()

    def check_assmps(self, assumptions, iterations, line_num):
        """Checks recursively if the inputs fulfil the assumptions

        :param assumptions: assumption to check
        :param iterations: how many iterations have to be done for the current assumption
        :param line_num: current line number of the input file
        :param has_error: if an error has been found
        :return: if an error has been found
        """
        has_error = False
        for _ in range(iterations):
            for assmp in assumptions:
                if isinstance(assmp, InputAssumptionLattice):
                    (err, line_num) = self.check_assmps(assmp.assmps, assmp.iterations, line_num)
                else:
                    line_num += 1
                    input_line = self.input_file.readline().strip()
                    err = self.check_one_assmp(assmp, input_line, line_num)
                has_error |= err
        return has_error, line_num

    def check_one_assmp(self, assumption: AssumptionLattice, input_line: str, line_num: int):
        """Checks if the current input fulfils the assumption

        :param assumption: current assumption
        :param input_line: current input
        :param line_num: current line number of input
        :return: if an error has been found
        """
        type_assmp = assumption.type_assumption
        if type_assmp == TypeLattice().integer():
            try:
                val = int(input_line)
            except ValueError:
                self.write_type_error(line_num, input_line, type_assmp)
                return True
        if type_assmp == TypeLattice().real():
            try:
                val = float(input_line)
            except ValueError:
                self.write_type_error(line_num, input_line, type_assmp)
                return True
        range_assmp = assumption.range_assumption
        if val < range_assmp.lower or val > range_assmp.upper:
            lower = range_assmp.lower
            upper = range_assmp.upper
            self.write_range_error(line_num, input_line, lower, upper)
            return True
        return False
