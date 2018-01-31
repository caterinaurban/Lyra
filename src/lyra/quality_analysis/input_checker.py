from lyra.abstract_domains.quality.assumption_lattice import TypeLattice
from lyra.quality_analysis.input_assmp_simplification import CheckerExpression, \
    CheckerAssumption, CheckerMultiAssumption


class ErrorInformation:
    """Contains information about an error."""
    def __init__(self, location, old_value, rel_val, error_message, assumption):
        self.location = location
        self.old_value = old_value
        self.new_value = old_value
        self.rel_val = rel_val
        self.error_message = error_message
        self.assumption = assumption


class InputChecker:
    """
    Checks an input file for errors using a JSON file created by a previously run
    assumption analysis
    """

    def __init__(self, input_file_path, input_file_name, program_name):
        self.error_file_name = f"{input_file_path}errors_{program_name}.txt"
        self.input_file_name = f"{input_file_path}{input_file_name}"
        self.error_file = None
        self.input_file = None
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
        """ Creates an error messages because of a wrong type."""
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
        """ Creates an error messages because of a wrong range."""
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

    def create_relation_error(self, line_num: int, relation: str, relation_evaluated: str):
        """Creates an error messages because of a wrong relation."""
        return f'Relation Error in line {line_num}: ' \
               f'expected: ({relation}) but found: ({relation_evaluated}).'

    def write_relation_error(self, line_num: int, relation: str, relation_evaluated: str):
        """Prints an error because a relation is violated

        :param line_num: line number of the input
        :param relation: the violated relation
        :param relation_evaluated: the violated relation and variables replaced with number
        """
        error = self.create_relation_error(line_num, relation, relation_evaluated)
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

    def check_input(self, assumptions, inputs: [str]):
        """Checks if the input file fulfils all the assumptions

        :param assumptions: all assumptions
        :param inputs: list of inputs that need to be stored for relation checking
        """
        self.error_file = open(self.error_file_name, "w")
        self.input_file = open(self.input_file_name, "r")
        self.errors = []
        input_saving = {}
        for an_input in inputs:
            input_saving[an_input] = None
        one_iter = CheckerExpression(True, None, 1)
        self.check_assmps(assumptions, one_iter, 0, input_saving)
        if len(self.errors) == 0:
            self.write_no_error()
        self.error_file.close()
        self.input_file.close()
        return self.errors

    def check_assmps(self, assumptions, iterations: CheckerExpression, line_num, inputs):
        """Checks recursively if the inputs fulfil the assumptions

        :param assumptions: assumption to check
        :param iterations: how many iterations have to be done for the current assumption
        :param line_num: current line number of the input file
        :param inputs: dictionary to store values of inputs for relation checking
        :return: if an error has been found
        """
        num_iter = iterations.evaluate(inputs)
        if num_iter is None:
            return None
        for _ in range(num_iter):
            for assmp in assumptions:
                if isinstance(assmp, CheckerMultiAssumption):
                    line_num = self.check_assmps(assmp.assmps, assmp.iterations, line_num, inputs)
                    if line_num is None:
                        return None
                else:
                    line_num += 1
                    input_line = self.input_file.readline().strip()
                    self.check_one_assmp(assmp, input_line, line_num, inputs)
        return line_num

    def check_one_assmp(self, assmp: CheckerAssumption, input_line: str, line_num, inputs):
        """Checks if the current input fulfils the assumption

        :param assmp: current assumption
        :param input_line: current input
        :param line_num: current line number of input
        :param inputs: dictionary of stored values for relation checking
        :return: if an error has been found
        """
        type_assmp = assmp.assmps.type_assumption
        if type_assmp == TypeLattice().integer():
            try:
                val = int(input_line)
            except ValueError:
                err_message = self.write_type_error(line_num, input_line, type_assmp)
                new_error = ErrorInformation(line_num, input_line, None, err_message, assmp)
                self.errors.append(new_error)
                return
        elif type_assmp == TypeLattice().real():
            try:
                val = float(input_line)
            except ValueError:
                err_message = self.write_type_error(line_num, input_line, type_assmp)
                new_error = ErrorInformation(line_num, input_line, None, err_message, assmp)
                self.errors.append(new_error)
                return
        else:
            return

        if assmp.var_id in inputs:
            inputs[assmp.var_id] = val

        relations = assmp.relations
        for relation in relations:
            other_val = inputs[relation.other_id]
            if not relation.evaluate(val, other_val):
                rel_with_vars = relation.user_friendly_relation_with_vars()
                rel_with_nums = relation.user_friendly_relation(val, other_val)
                err_message = self.write_relation_error(line_num, rel_with_vars, rel_with_nums)
                new_error = ErrorInformation(line_num, input_line, other_val, err_message, assmp)
                self.errors.append(new_error)

    def check_assmp(self, error: ErrorInformation):
        """Checks if a value fulfils an assumption

        :param error: the current error that should be checked
        :return: the error with an adapted error message or None if no error was found
        """
        type_assmp = error.assumption.assmps.type_assumption
        if type_assmp == TypeLattice().integer():
            try:
                val = int(error.new_value)
            except ValueError:
                message = self.create_type_error(error.location, error.new_value, type_assmp)
                error.error_message = message
                return error
        elif type_assmp == TypeLattice().real():
            try:
                val = float(error.new_value)
            except ValueError:
                message = self.create_type_error(error.location, error.new_value, type_assmp)
                error.error_message = message
                return error
        else:
            return None

        relations = error.assumption.relations
        for relation in relations:
            other_val = error.rel_val
            if not relation.evaluate(val, other_val):
                rel_vars = relation.user_friendly_relation_with_vars()
                rel_nums = relation.user_friendly_relation(val, other_val)
                message = self.create_relation_error(error.location, rel_vars, rel_nums)
                error.error_message = message
                return error
        return None
