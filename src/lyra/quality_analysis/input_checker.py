from enum import IntEnum
from math import inf

from lyra.abstract_domains.quality.assumption_lattice import TypeLattice
from lyra.quality_analysis.input_assmp_simplification import CheckerExpression, \
    CheckerAssumption, CheckerMultiAssumption, CheckerLengthIdentifier, CheckerZeroIdentifier


class ErrorInformation:
    """Contains information about an error."""
    def __init__(self, error_location, value, error_message, assumption, error_level):
        self.location = error_location
        self.value = value
        self.error_message = error_message
        self.assumption = assumption
        self.error_level = error_level
        self.relation = None
        self.rel_val = None
        self.rel_location = None
        self.rel_assmp = None
        self.is_first_val = True

    def add_rel_info(self, relation, rel_value: str, rel_loccation: int, rel_assmp):
        """Adds relational info to the error.

        :param relation: relation that caused an error
        :param rel_value: value of the second value
        :param rel_loccation: location of the second value
        :param rel_assmp: non relational assumptions of the second value
        :return:
        """
        self.relation = relation
        self.rel_val = rel_value
        self.rel_location = rel_loccation
        self.rel_assmp = rel_assmp

    class ErrorLevel(IntEnum):
        """Info about the Level of the error."""
        Relation = 3
        Range = 2
        Type = 1
        Missing = 0


class InputChecker:
    """Checks an input file for errors using a JSON file created by a previously run
    assumption analysis."""
    def __init__(self, input_file_path, input_file_name, program_name):
        self.error_file_name = f"{input_file_path}errors_{program_name}.txt"
        self.input_file_name = f"{input_file_path}{input_file_name}"
        self.error_file = None
        self.input_file = None
        self.inputs = {}

    def write_missing_error(self, num_values_expected, num_values_found, line_num=None, delm=None):
        """Prints an error because there are more assumptions than values

        :param num_values_expected: number of values that are exptected
        :param num_values_found: number of values that were found in input file
        :param line_num: line number if the error occurs on a specific line
        :param delm: delimiter if error occured on a single line
        """
        line_err = f"in line {line_num+1}" if line_num is not None else ""
        delimiter = ""
        if delimiter is not None:
            delimiter = "separated by whitespaces" if delm == "" else f"separated by '{delm}'"
        error = f"Missing value {line_err}:\n" \
                f"expected at least {num_values_expected} values {delimiter}\n" \
                f"instead found {num_values_found}."
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_general_error(self, type_assmp, range_assmp, relations) -> str:
        """Create a general message what is expected from an input value

        :param type_assmp: expected type
        :param range_assmp: expected range
        :param relations: expected relations
        :return: general string with info about expected assumptions
        """
        if type_assmp.is_top():
            return ""
        error = f"expected one value of type {self.type_to_type_name(type_assmp)}"
        if not range_assmp.is_top():
            error += f"\nin range [{range_assmp.lower}, {range_assmp.upper}]"
        if relations is not None and len(relations) > 0:
            error += f"\nwith relation {relations}"
        return error

    def create_type_error(self, line_num, input_line, type_assmp, range_assmp, relations):
        """ Creates an error messages because of a wrong type."""
        expected = self.create_general_error(type_assmp, range_assmp, relations)
        return f"Type Error in line {line_num+1}: {expected}\ninstead found \'{input_line}\'."

    def write_type_error(self, line_num, input_line, type_assmp, range_assmp, relations):
        """Prints an error because an input is not of an expected type

        :param line_num: line number of the input
        :param input_line: input that contains the error
        :param type_assmp: type assumption of the input
        :param range_assmp: range assumption of the input
        :param relations: the relational assumptions of the input
        """
        error = self.create_type_error(line_num, input_line, type_assmp, range_assmp, relations)
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_range_error(self, line_num, input_line, type_assmp, range_assmp, relations):
        """ Creates an error messages because of a wrong range."""
        expected = self.create_general_error(type_assmp, range_assmp, relations)
        return f"Range Error in line {line_num+1}: {expected}\ninstead found '{input_line}'."

    def write_range_error(self, line_num, input_line, type_assmp, range_assmp, relations):
        """Prints an error because an input is not in an expected range

        :param line_num: line number of the input
        :param input_line: input that contains the error
        :param type_assmp: type assumption of the input
        :param range_assmp: range assumption of the input
        :param relations: the relational assumptions of the input
        """
        error = self.create_range_error(line_num, input_line, type_assmp, range_assmp, relations)
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_relation_error(self, line_num, assmps1, assmps2, relation, rel_eval):
        """Creates an error messages because of a wrong relation."""
        if assmps1 is None:
            assmp1 = ""
        elif isinstance(assmps1, CheckerMultiAssumption):
            if assmps1.delimiter == "":
                delimiter = "whitespaces"
            else:
                delimiter = f"delimiter '{assmps1.delimiter}'"
            assmp1 = f"expected values separated by {delimiter}"
        else:
            type_assmp = assmps1.assmp.type_assumption
            range_assmp = assmps1.assmp.range_assumption
            assmp1 = self.create_general_error(type_assmp, range_assmp, [])
        if assmps2 is None:
            assmp2 = ""
        elif isinstance(assmps2, CheckerMultiAssumption):
            if assmps2.delimiter == "":
                delimiter = "whitespaces"
            else:
                delimiter = f"delimiter '{assmps2.delimiter}'"
            assmp2 = f"expected values separated by {delimiter}"
        else:
            type_assmp = assmps2.assmp.type_assumption
            range_assmp = assmps2.assmp.range_assumption
            assmp2 = self.create_general_error(type_assmp, range_assmp, [])
        assmps_val1 = f"value1: {assmp1}\n" if assmp1 != "" else ""
        assmps_val2 = f"value2: {assmp2}\n" if assmp2 != "" else ""
        return f"Relation Error in line {line_num+1}:\n" \
               f"{assmps_val1}" \
               f"{assmps_val2}" \
               f"with relation {relation}\n" \
               f"instead found: ({rel_eval})."

    def write_relation_error(self, line_num, assmps1, assmps2, relation, rel_eval):
        """Prints an error because a relation is violated

        :param line_num: line number of the input
        :param assmps1: assumption of the first relation input
        :param assmps2: assumption of the second relation input
        :param relation: the relational assumption of the inputs
        :param rel_eval: the violated relation and variables replaced with number
        """
        error = self.create_relation_error(line_num, assmps1, assmps2, relation, rel_eval)
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def write_no_error(self):
        """Prints a message that no error has been found
        """
        error = f'The input data did not violate any assumptions found by the analyzer.'
        self.error_file.write(error)
        self.error_file.write('\n')

    def type_to_type_name(self, type_assmp: TypeLattice) -> str:
        """Returns the name of the type, given an element of the TypeLattice

        :param type_assmp: type that should be converted to its name
        :return: the name of the type
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
        errors = []
        self.inputs = {}
        for an_input in inputs:
            self.inputs[an_input] = None
        self.inputs[CheckerZeroIdentifier()] = (0, None, None)
        one_iter = CheckerExpression(True, None, 1)
        self.check_assmps(assumptions, one_iter, -1, None, errors)
        if len(errors) == 0:
            self.write_no_error()
        self.error_file.close()
        self.input_file.close()
        return errors

    def check_assmps(self, assumptions, iters: CheckerExpression, line, delimiter, errors):
        """Checks recursively if the inputs fulfil the assumptions

        :param assumptions: assumption to check
        :param iters: how many iterations have to be done for the current assumption
        :param line: current line number of the input file
        :param delimiter: if None the current assumptions will be interpreted to be for values
        on the same line using the delimiter
        :param errors: keeps track of all errors found by the input checker
        :return: if an error has been found
        """
        if delimiter is not None:
            num_iter = iters.evaluate(self.inputs)

            line += 1
            curr_input = self.input_file.readline().strip()
            if num_iter is None:
                return line

            if delimiter != "":
                values = curr_input.split(delimiter)
            else:
                values = curr_input.split()

            assmp = assumptions.assmps[0]
            len_id = CheckerLengthIdentifier(assmp.var_id.input_id)
            if len_id in self.inputs:
                self.inputs[len_id] = (len(values), line, assumptions)

            if len(values) < num_iter:
                msg = self.write_missing_error(num_iter, len(values), line, delimiter)
                err_lvl = ErrorInformation.ErrorLevel.Missing
                new_error = ErrorInformation(line, curr_input, msg, assmp, err_lvl)
                errors.append(new_error)
                return line
            for relation in assmp.relations:
                other_id = relation.get_other_id(len_id)
                rel_val = self.inputs[other_id]
                if rel_val is None:
                    continue
                if not relation.evaluate((len_id, len(values)), (other_id, rel_val[0])):
                    rel_eval = relation.user_friendly_relation(len(values), rel_val[0])
                    rel_vars = relation.user_friendly_relation_with_vars()
                    rel_assmp = rel_val[2]
                    assmps = assumptions
                    msg = self.write_relation_error(line, assmps, rel_assmp, rel_vars, rel_eval)
                    lvl = ErrorInformation.ErrorLevel.Relation
                    new_error = ErrorInformation(line, curr_input, msg, assumptions, lvl)
                    new_error.add_rel_info(relation, str(rel_val[0]), rel_val[1], rel_assmp)
                    errors.append(new_error)
        else:
            num_iter = iters.evaluate(self.inputs)
            if num_iter is None:
                return None
            for _ in range(num_iter):
                for assmp in assumptions:
                    if isinstance(assmp, CheckerMultiAssumption):
                        delm = assmp.delimiter
                        if delm is not None:
                            assmps = assmp
                        else:
                            assmps = assmp.assmps
                        next_iters = assmp.iterations
                        line = self.check_assmps(assmps, next_iters, line, delm, errors)
                        if line is None:
                            return None
                    else:
                        line += 1
                        input_line = self.input_file.readline().strip()
                        error = self.check_one_assmp(assmp, input_line, line)
                        if error is not None:
                            errors.append(error)
        return line

    def check_one_assmp(self, assmp: CheckerAssumption, in_val: str, line: int):
        """Checks if the current input fulfils the assumption

        :param assmp: current assumption
        :param in_val: current input
        :param line: current line number of input
        :return: if an error has been found
        """
        type_assmp = assmp.assmp.type_assumption
        range_assmp = assmp.assmp.range_assumption
        relations = assmp.relations

        if type_assmp == TypeLattice().integer():
            try:
                val = int(in_val)
            except ValueError:
                message = self.write_type_error(line, in_val, type_assmp, range_assmp, relations)
                err_lvl = ErrorInformation.ErrorLevel.Type
                new_error = ErrorInformation(line, in_val, message, assmp, err_lvl)
                return new_error
        elif type_assmp == TypeLattice().real():
            try:
                val = float(in_val)
            except ValueError:
                message = self.write_type_error(line, in_val, type_assmp, range_assmp, relations)
                err_lvl = ErrorInformation.ErrorLevel.Type
                new_error = ErrorInformation(line, in_val, message, assmp, err_lvl)
                return new_error
        else:
            val = in_val

        input_id = assmp.var_id

        if input_id in self.inputs:
            self.inputs[input_id] = (val, line, assmp)

        if range_assmp.lower != -inf or range_assmp.upper != inf:
            if val < range_assmp.lower or val > range_assmp.upper:
                err_msg = self.write_range_error(line, in_val, type_assmp, range_assmp, relations)
                err_lvl = ErrorInformation.ErrorLevel.Type
                new_error = ErrorInformation(line, in_val, err_msg, assmp, err_lvl)
                return new_error

        for relation in relations:
            other_id = relation.get_other_id(input_id)
            rel_val = self.inputs[other_id]
            if rel_val is None:
                continue
            if not relation.evaluate((input_id, val), (other_id, rel_val[0])):
                rel_eval = relation.user_friendly_relation(val, rel_val[0])
                msg = self.write_relation_error(line, assmp, rel_val[2], relation, rel_eval)
                lvl = ErrorInformation.ErrorLevel.Relation
                new_error = ErrorInformation(line, in_val, msg, assmp, lvl)
                new_error.add_rel_info(relation, str(rel_val[0]), rel_val[1], rel_val[2])
                if isinstance(relation.this_id, CheckerZeroIdentifier):
                    new_error.is_first_val = False
                return new_error

        return None

    def check_new_value(self, error: ErrorInformation):
        """Checks if an error is now fulfiled with the new value

        :param error: error to check
        :return: a new error if one is found, otherwise None.
        """
        if error.relation is None or error.is_first_val:
            if isinstance(error.assumption, CheckerMultiAssumption):
                delimiter = error.assumption.delimiter
                if delimiter != "":
                    values = error.value.split(delimiter)
                else:
                    values = error.value.split()
                for value in values:
                    assmps = error.assumption.assmps[0]
                    val = self.check_non_relational_assmps(value, assmps, error)
                    if isinstance(val, ErrorInformation.ErrorLevel):
                        return error
                error.is_first_val = False
                return None
            if isinstance(error.assumption.var_id, CheckerZeroIdentifier):
                error.is_first_val = False
                return None
            val = self.check_non_relational_assmps(error.value, error.assumption, error)
            if isinstance(val, ErrorInformation.ErrorLevel):
                return error
            error.is_first_val = False
            return None

        if isinstance(error.rel_assmp, CheckerMultiAssumption):
            delimiter = error.rel_assmp.delimiter
            if delimiter != "":
                values = error.rel_val.split(delimiter)
            else:
                values = error.rel_val.split()
            for value in values:
                val = self.check_non_relational_assmps(value, error.rel_assmp.assmps[0], error)
                if isinstance(val, ErrorInformation.ErrorLevel):
                    return error
        elif not isinstance(error.rel_val, CheckerZeroIdentifier):
            val = self.check_non_relational_assmps(error.rel_val, error.rel_assmp, error)
            if isinstance(val, ErrorInformation.ErrorLevel):
                return error

        eval_value = self.evaluate_value(error.value, error.assumption)
        eval_other_value = self.evaluate_value(error.rel_val, error.rel_assmp)
        relation = error.relation
        if not relation.evaluate(eval_value, eval_other_value):
            rel = relation.user_friendly_relation(eval_value[1], eval_other_value[1])
            rel_str = relation.user_friendly_relation_with_vars()
            loc = error.location
            assmp1 = error.assumption
            message = self.create_relation_error(loc, assmp1, error.rel_assmp, rel_str, rel)
            error.error_message = message
            return error
        return None

    def evaluate_value(self, value: str, assmp):
        """Turns a value into the correct type.

        :param value: value to be evaluated
        :param assmp: assumption of the input value
        :return: tuple (input id, value) of the evaluated value
        """
        if isinstance(assmp, CheckerMultiAssumption):
            delimiter = assmp.delimiter
            var_id = CheckerLengthIdentifier(assmp.assmps[0].var_id.input_id)
            if assmp.delimiter != "":
                return var_id, len(value.split(delimiter))
            else:
                return var_id, len(value.split())
        if isinstance(assmp.var_id, CheckerZeroIdentifier):
            return CheckerZeroIdentifier(), 0
        type_assmp = assmp.assmp.type_assumption
        if type_assmp == TypeLattice().integer():
            return assmp.var_id, int(value)
        if type_assmp == TypeLattice().real():
            return assmp.var_id, float(value)
        return assmp.var_id, value

    def check_non_relational_assmps(self, value: str, assmps, error: ErrorInformation):
        """Checks if an input fulfils the non relational assumptions

        :param value: input to check
        :param assmps: assumptions about the input
        :param error: current error of the input
        :return: ErrorLevel if an error is found, otherwise the casted value
        """
        type_assmp = assmps.assmp.type_assumption
        range_assmp = assmps.assmp.range_assumption
        error_level = None
        val = None
        if type_assmp == TypeLattice().integer():
            try:
                val = int(value)
            except ValueError:
                error_level = ErrorInformation.ErrorLevel.Type
        elif type_assmp == TypeLattice().real():
            try:
                val = float(value)
            except ValueError:
                error_level = ErrorInformation.ErrorLevel.Type
        else:
            return value

        if error_level is None and (val < range_assmp.lower or val > range_assmp.upper):
            error_level = ErrorInformation.ErrorLevel.Range

        if error_level is not None:
            loc = error.location
            new_val = error.value
            error.error_level = error_level
            relations = assmps.relations
            if error_level == ErrorInformation.ErrorLevel.Type:
                message = self.create_type_error(loc, new_val, type_assmp, range_assmp, relations)
            else:
                message = self.create_range_error(loc, new_val, type_assmp, range_assmp, relations)
            error.error_message = message
            return error_level

        return val
