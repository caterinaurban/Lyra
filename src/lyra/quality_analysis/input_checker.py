from lyra.abstract_domains.quality.assumption_lattice import TypeLattice, AssumptionLattice, \
    InputAssumptionLattice


class InputChecker:
    """
    Checks an input file for errors using a JSON file created by a previously run
    assumption analysis
    """

    def __init__(self, input_file_path, input_file_name, program_name):
        self.error_file = open(f"{input_file_path}errors_{program_name}.txt", "w")
        self.input_file = open(f"{input_file_path}{input_file_name}", "r")
        self.errors = []

    def write_missing_error(self, num_values_expected, num_values_found):
        """Prints an error because there are more assumptions than values

        :param num_values_expected: number of values that are exptected
        :param num_values_found: number of values that were found in input file
        """
        error = f'Missing value: ' \
                f'expected at least {num_values_expected} values instead found {num_values_found}.'
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_type_error(self, line_num, input_line, type_assmp):
        return f'Type Error in line {line_num}: ' \
                f'expected one value of type {self.type_to_type_name(type_assmp)} ' \
                f'instead found \'{input_line}\'.'

    def write_type_error(self, line_num, input_line, type_assmp):
        """Prints an error because an input is not of an expected type

        :param line_num: line number of the input
        :param input_line: input that contains the error
        :param type_assmp: expected type
        """
        error = self.create_type_error(line_num, input_line, type_assmp)
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_range_error(self, line_num, input_line, lower, upper):
        return f'Range Error in line {line_num}: ' \
                f'expected one value in range [{lower}, {upper}] ' \
                f'instead found \'{input_line}\'.'

    def write_range_error(self, line_num, input_line, lower, upper):
        """Prints an error because an input is not in an expected range

        :param line_num: line number of the input
        :param input_line: input that contains the error
        :param lower: expected lower bound
        :param upper: exptected upper bound
        """
        error = self.create_range_error(line_num, input_line, lower, upper)
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def write_no_error(self):
        """Prints a message that no error has been found
        """
        error = f'The input data did not violate any assumptions found by the analyzer.'
        self.error_file.write(error)
        self.error_file.write('\n')

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

    def count_values(self):
        """Count the number of lines in the input file

        :return: number of lines found
        """
        input_file = open(self.input_file.name, 'r')
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

    def check_input(self, assumptions: []):
        """Checks if the input file fulfils all the assumptions

        :param assumptions: all assumptions
        """
        num_values = self.count_values()
        num_total_assmps = self.find_num_total_assmps(assumptions, 1)
        if num_values < num_total_assmps:
            self.write_missing_error(num_total_assmps, num_values)
        (has_errors, _) = self.check_assmps(assumptions, 1, 0)
        if not has_errors:
            self.write_no_error()
        self.error_file.close()
        self.input_file.close()
        return self.errors

    def check_assmps(self, assumptions, iterations, line_num):
        """Checks recursively if the inputs fulfil the assumptions

        :param assumptions: assumption to check
        :param iterations: how many iterations have to be done for the current assumption
        :param line_num: current line number of the input file
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
                error_message = self.write_type_error(line_num, input_line, type_assmp)
                new_error = ErrorInformation(line_num, input_line, error_message, assumption)
                self.errors.append(new_error)
                return True
        elif type_assmp == TypeLattice().real():
            try:
                val = float(input_line)
            except ValueError:
                error_message = self.write_type_error(line_num, input_line, type_assmp)
                new_error = ErrorInformation(line_num, input_line, error_message, assumption)
                self.errors.append(new_error)
                return True
        else:
            return False

        range_assmp = assumption.range_assumption
        if val < range_assmp.lower or val > range_assmp.upper:
            lower = range_assmp.lower
            upper = range_assmp.upper
            error_message = self.write_range_error(line_num, input_line, lower, upper)
            new_error = ErrorInformation(line_num, input_line, error_message, assumption)
            self.errors.append(new_error)
            return True
        return False

    def check_assmp(self, assumption: AssumptionLattice, value, line_num):
        type_assmp = assumption.type_assumption
        if type_assmp == TypeLattice().integer():
            try:
                val = int(value)
            except ValueError:
                error_message = self.create_type_error(line_num, value, type_assmp)
                return ErrorInformation(line_num, value, error_message, assumption)
        elif type_assmp == TypeLattice().real():
            try:
                val = float(value)
            except ValueError:
                error_message = self.create_type_error(line_num, value, type_assmp)
                return ErrorInformation(line_num, value, error_message, assumption)
        else:
            return None

        range_assmp = assumption.range_assumption
        if val < range_assmp.lower or val > range_assmp.upper:
            lower = range_assmp.lower
            upper = range_assmp.upper
            error_message = self.create_range_error(line_num, value, lower, upper)
            return ErrorInformation(line_num, value, error_message, assumption)
        return None


class ErrorInformation:

    def __init__(self, location, old_value, error_message, assumption):
        self.location = location
        self.old_value = old_value
        self.new_value = old_value
        self.error_message = error_message
        self.assumption = assumption
