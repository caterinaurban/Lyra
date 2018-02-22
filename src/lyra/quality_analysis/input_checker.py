from enum import IntEnum
from math import inf

from lyra.abstract_domains.quality.assumption_lattice import TypeLattice
from lyra.quality_analysis.input_assmp_simplification import CheckerExpression, \
    CheckerAssumption, CheckerMultiAssumption, CheckerLengthIdentifier, CheckerZeroIdentifier


class InputLocation:
    """Location of an input value"""
    def __init__(self, line: int, column, input_id):
        self._line = line
        self.column = column
        self.input_id = input_id

    @property
    def user_line(self):
        return self._line+1

    @property
    def file_line(self):
        return self._line

    def add_lines(self, num: int):
        self._line += num
        return self

    def sub_lines(self, num: int):
        self._line -= num
        return self

    def user_repr(self):
        """Returns a representation of the input location for the user."""
        if isinstance(self.input_id, CheckerLengthIdentifier):
            return f"(number of elements in Line {self.user_line})"
        else:
            return f"(value in {self.__repr__()})"

    def __hash__(self):
        return hash((self._line, self.column, self.input_id))

    def __eq__(self, other):
        same_loc = self.file_line == other.file_line and self.column == other.column
        return same_loc and self.input_id == other.input_id

    def __lt__(self, other):
        if self.file_line < other.file_line:
            return True
        return self.file_line == other.file_line and self.column < other.column

    def __repr__(self):
        rep = f"Line {self.user_line}"
        if self.column is not None:
            rep += f", Column {self.column}"
        return rep


class InputInfo:
    """Information about an input."""
    def __init__(self, value, location: InputLocation, assmp, prev_line=None, next_line=None):
        self._value_orig = value
        self._value = None
        self.var_id = None
        self.assmp = assmp
        self.location = location
        self.evaluate_value()
        self.prev_line = prev_line
        self.next_line = next_line

    @property
    def eval_value(self):
        return self._value

    @property
    def orig_value(self):
        return self._value_orig

    def change_orig_value(self, new_value):
        """Changes the value of the original value and evaluates it.

        :param new_value: new value
        """
        self._value_orig = new_value
        self.evaluate_value()

    def check_type(self, new_value) -> bool:
        """Checks if the given value corresponds to the type of the assumption

        :param new_value: new value to be checked
        :return: True if the the value is of the correct type
        """
        if not isinstance(self.assmp, CheckerMultiAssumption):
            type_assmp = self.assmp.assmp.type_assumption
            try:
                if type_assmp == TypeLattice().integer():
                    int(new_value)
                elif type_assmp == TypeLattice().real():
                    float(new_value)
            except ValueError:
                return False
        return True

    def evaluate_value(self):
        """Evaluates the input value to the correct type."""
        if isinstance(self.assmp, CheckerMultiAssumption):
            delimiter = self.assmp.delimiter
            if self.assmp.delimiter != "":
                self._value = len(self._value_orig.split(delimiter))
            else:
                self._value = len(self._value_orig.split())
            self.var_id = CheckerLengthIdentifier(self.assmp.assmps[0].var_id.input_id)
        else:
            if self.assmp is None:
                self._value = 0
                self.var_id = CheckerZeroIdentifier()
                return
            self.var_id = self.assmp.var_id
            type_assmp = self.assmp.assmp.type_assumption
            try:
                if type_assmp == TypeLattice().integer():
                    self._value = int(self._value_orig)
                elif type_assmp == TypeLattice().real():
                    self._value = float(self._value_orig)
            except ValueError:
                self._value = self.orig_value


class ErrorInformation:
    """Contains information about an error."""
    def __init__(self, input_infos1: InputInfo, error_message, error_level):
        self.infos1 = input_infos1
        self.infos2 = None
        self.error_message = error_message
        self.error_level = error_level
        self.relation = None
        self.is_first_val = True

    def add_rel_info(self, relation, rel_info: InputInfo):
        """Adds relational info to the error.

        :param relation: relation that caused an error
        :param rel_info: information about the relation value
        :return:
        """
        self.relation = relation
        self.infos2 = rel_info

    def create_info_msg(self, is_first: bool) -> str:
        """Creates an info message about the assumptions of the first or second value

        :param is_first: True if a message for the assumptions of the first value should be
        created, False if a message for the second value's assummptions should be created
        :return: an info message about the value's assumptions
        """
        if is_first and isinstance(self.infos1.assmp, CheckerMultiAssumption):
            if self.infos1.assmp.delimiter == "":
                delm = "whitespaces"
            else:
                delm = f"'{self.infos1.assmp.delimiter}'"
            return f"Type: List of values\nseparated by {delm}"
        if not is_first and isinstance(self.infos2.assmp, CheckerMultiAssumption):
            if self.infos2.assmp.delimiter == "":
                delm = "whitespaces"
            else:
                delm = f"'{self.infos2.assmp.delimiter}'"
            return f"Type: List of values\nseparated by {delm}"

        assmp = self.infos1.assmp.assmp if is_first else self.infos2.assmp.assmp
        msg = ""
        if not assmp.type_assumption.is_top():
            msg = f"Type: {self.type_to_type_name(assmp.type_assumption)}"
        if not assmp.range_assumption.is_top():
            msg += f"\nRange: [{assmp.range_assumption.lower}, {assmp.range_assumption.upper}]"
        return msg

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
        self.prev_line = ""
        self.eof_reached = False

    def write_missing_error(self, num_values_expected, num_values_found, loc=None, delm=None):
        """Prints an error because there are more assumptions than values

        :param num_values_expected: number of values that are exptected
        :param num_values_found: number of values that were found in input file
        :param loc: location if the error occurs on a specific line
        :param delm: delimiter if error occured on a single line
        """
        line_err = f"in {loc}" if loc is not None else ""
        delimiter = ""
        if delimiter is not None:
            delimiter = "separated by whitespaces" if delm == "" else f"separated by '{delm}'"
        error = f"Missing value {line_err}:\n" \
                f"expected at least {num_values_expected} values {delimiter}\n" \
                f"instead found {num_values_found}."
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def write_missing_value_error(self, loc: InputLocation) -> str:
        """Creates and writes a simple missing value error.

        :param loc: location of the missing value
        :return: the error message
        """
        error = f"Missing value in {loc}"
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_type_error(self, loc, input_line, type_assmp):
        """ Creates an error messages because of a wrong type."""
        return f"Type Error in {loc}:\n" \
               f"expected: one value of type {self.type_to_type_name(type_assmp)}\n" \
               f"instead found: \'{input_line}\'."

    def write_type_error(self, loc, input_line, type_assmp):
        """Prints an error because an input is not of an expected type

        :param loc: location of the input
        :param input_line: input that contains the error
        :param type_assmp: type assumption of the input
        """
        error = self.create_type_error(loc, input_line, type_assmp)
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_range_error(self, loc, input_line, range_assmp):
        """ Creates an error messages because of a wrong range."""
        return f"Range Error in {loc}:\n" \
               f"expected: one value in range [{range_assmp.lower}, {range_assmp.upper}]\n" \
               f"instead found: '{input_line}'."

    def write_range_error(self, loc, input_line, range_assmp):
        """Prints an error because an input is not in an expected range

        :param loc: location of the input
        :param input_line: input that contains the error
        :param range_assmp: range assumption of the input
        """
        error = self.create_range_error(loc, input_line, range_assmp)
        self.error_file.write(error)
        self.error_file.write('\n')
        return error

    def create_relation_error(self, relation, rel_eval):
        """Creates an error messages because of a wrong relation."""
        return f"Relation Error:\n" \
               f"expected: {relation}\n" \
               f"instead found: ({rel_eval})."

    def write_relation_error(self, relation, rel_eval):
        """Prints an error because a relation is violated

        :param relation: the relational assumption of the inputs
        :param rel_eval: the violated relation and variables replaced with number
        """
        error = self.create_relation_error(relation, rel_eval)
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
        self.eof_reached = False
        errors = []
        self.inputs = {}
        self.prev_line = ""
        for an_input in inputs:
            self.inputs[an_input] = None
        self.inputs[CheckerZeroIdentifier()] = InputInfo(0, None, None, None, None)
        one_iter = CheckerExpression(True, None, 1)
        self.check_assmps(assumptions, one_iter, -1, None, errors)
        if len(errors) == 0:
            self.write_no_error()
        self.error_file.close()
        self.input_file.close()
        errors = sorted(errors, key=lambda err: (err.error_level, err.infos1.location))
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
            curr_input = self.input_file.readline()
            assmp = assumptions.assmps[0]
            if self.eof_reached or curr_input == "":
                err_lvl = ErrorInformation.ErrorLevel.Missing
                loc = InputLocation(line, None, assmp.var_id)
                input_info = InputInfo(curr_input, loc, assumptions, self.prev_line)
                err_msg = self.write_missing_value_error(loc)
                new_error = ErrorInformation(input_info, err_msg, err_lvl)
                errors.append(new_error)
                return line
            else:
                if not curr_input.endswith("\n"):
                    self.eof_reached = True
                curr_input = curr_input.strip()
                self.update_next_line_val(errors, curr_input)
                if num_iter is None:
                    return line

                if delimiter != "":
                    values = curr_input.split(delimiter)
                else:
                    values = curr_input.split()

                len_id = CheckerLengthIdentifier(assmp.var_id.input_id)
                loc = InputLocation(line, None, len_id)
                if len_id in self.inputs:
                    input_info = InputInfo(curr_input, loc, assumptions, self.prev_line, None)
                    self.inputs[len_id] = input_info

                if len(values) < num_iter:
                    msg = self.write_missing_error(num_iter, len(values), loc, delimiter)
                    err_lvl = ErrorInformation.ErrorLevel.Missing
                    input_info = InputInfo(curr_input, loc, assumptions, self.prev_line)
                    new_error = ErrorInformation(input_info, msg, err_lvl)
                    errors.append(new_error)
                    return line
                for relation in assmp.relations:
                    other_id = relation.get_other_id(len_id)
                    rel_val = self.inputs[other_id]
                    if rel_val is None:
                        continue
                    val1 = (len_id, len(values))
                    val2 = (other_id, rel_val.eval_value)
                    if not relation.evaluate(val1, val2):
                        val = len(values)
                        in_val = curr_input
                        rel = relation
                        mul_assmp = assumptions
                        e = self.rel_error(len_id, other_id, val, rel_val, rel, loc, mul_assmp, in_val)
                        errors.append(e)
            self.prev_line = curr_input
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
                        input_line = self.input_file.readline()
                        if self.eof_reached or input_line == "":
                            err_lvl = ErrorInformation.ErrorLevel.Missing
                            loc = InputLocation(line, None, assmp.var_id)
                            input_info = InputInfo(input_line, loc, assmp, self.prev_line)
                            err_msg = self.write_missing_value_error(loc)
                            new_error = ErrorInformation(input_info, err_msg, err_lvl)
                            errors.append(new_error)
                        else:
                            if not input_line.endswith("\n"):
                                self.eof_reached = True
                            input_line = input_line.strip()
                            self.update_next_line_val(errors, input_line)
                            error = self.check_one_assmp(assmp, input_line, line)
                            if error is not None:
                                if error.infos1.prev_line is None:
                                    error.infos1.prev_line = self.prev_line
                                errors.append(error)
                        self.prev_line = input_line
        return line

    def update_next_line_val(self, errors: [ErrorInformation], input_line: str):
        """Updates information about the next line of an input with an error

        :param errors: current errors
        :param input_line: current input
        """
        if len(errors) > 0 and errors[-1].infos1.next_line is None:
            errors[-1].infos1.next_line = input_line
        lines = [(i, v) for i, v in self.inputs.items() if v is not None and v.next_line is None]
        for input_id, input_val in lines:
            self.inputs[input_id].next_line = input_line

    def check_one_assmp(self, assmp: CheckerAssumption, in_val: str, line: int):
        """Checks if the current input fulfils the assumption

        :param assmp: current assumption
        :param in_val: current input
        :param line: line number of the current input
        :return: if an error has been found
        """
        type_assmp = assmp.assmp.type_assumption
        range_assmp = assmp.assmp.range_assumption
        relations = assmp.relations

        input_id = assmp.var_id
        loc = InputLocation(line, None, input_id)

        if type_assmp == TypeLattice().integer():
            try:
                val = int(in_val)
            except ValueError:
                message = self.write_type_error(loc, in_val, type_assmp)
                err_lvl = ErrorInformation.ErrorLevel.Type
                input_info = InputInfo(in_val, loc, assmp)
                new_error = ErrorInformation(input_info, message, err_lvl)
                return new_error
        elif type_assmp == TypeLattice().real():
            try:
                val = float(in_val)
            except ValueError:
                message = self.write_type_error(loc, in_val, type_assmp)
                err_lvl = ErrorInformation.ErrorLevel.Type
                input_info = InputInfo(in_val, loc, assmp)
                new_error = ErrorInformation(input_info, message, err_lvl)
                return new_error
        else:
            val = in_val

        if input_id in self.inputs:
            input_info = InputInfo(val, loc, assmp, self.prev_line, None)
            self.inputs[input_id] = input_info

        if range_assmp.lower != -inf or range_assmp.upper != inf:
            if val < range_assmp.lower or val > range_assmp.upper:
                err_msg = self.write_range_error(loc, in_val, range_assmp)
                err_lvl = ErrorInformation.ErrorLevel.Type
                input_info = InputInfo(in_val, loc, assmp)
                new_error = ErrorInformation(input_info, err_msg, err_lvl)
                return new_error

        for relation in relations:
            other_id = relation.get_other_id(input_id)
            rel_inf = self.inputs[other_id]
            if rel_inf is None:
                continue
            val1 = (input_id, val)
            val2 = (other_id, rel_inf.eval_value)
            if not relation.evaluate(val1, val2):
                e = self.rel_error(input_id, other_id, val, rel_inf, relation, loc, assmp, in_val)
                return e

        return None

    def check_new_value(self, error: ErrorInformation):
        """Checks if an error is now fulfiled with the new value

        :param error: error to check
        :return: a new error if one is found, otherwise None.
        """
        input_info = error.infos1
        if error.relation is None or error.is_first_val:
            if isinstance(input_info.assmp, CheckerMultiAssumption):
                delimiter = input_info.assmp.delimiter
                if delimiter != "":
                    values = input_info.orig_value.split(delimiter)
                else:
                    values = input_info.orig_value.split()
                for value in values:
                    assmps = input_info.assmp.assmps[0]
                    val = self.check_non_relational_assmps(value, assmps, error)
                    if isinstance(val, ErrorInformation.ErrorLevel):
                        return error
                error.is_first_val = False
                return None
            if isinstance(input_info.assmp.var_id, CheckerZeroIdentifier):
                error.is_first_val = False
                return None
            val = self.check_non_relational_assmps(input_info.eval_value, input_info.assmp, error)
            if isinstance(val, ErrorInformation.ErrorLevel):
                return error
            error.is_first_val = False

        rel_input_info = error.infos2
        if rel_input_info is None:
            return None
        if isinstance(rel_input_info.assmp, CheckerMultiAssumption):
            delimiter = rel_input_info.assmp.delimiter
            if delimiter != "":
                values = rel_input_info.orig_value.split(delimiter)
            else:
                values = rel_input_info.orig_value.split()
            for value in values:
                assmps = rel_input_info.assmp.assmps[0]
                val = self.check_non_relational_assmps(value, assmps, error)
                if isinstance(val, ErrorInformation.ErrorLevel):
                    return error
        elif not isinstance(rel_input_info.var_id, CheckerZeroIdentifier):
            assmp = rel_input_info.assmp
            val = self.check_non_relational_assmps(rel_input_info.orig_value, assmp, error)
            if isinstance(val, ErrorInformation.ErrorLevel):
                return error

        eval_value = input_info.var_id, input_info.eval_value
        eval_other_value = rel_input_info.var_id, rel_input_info.eval_value
        relation = error.relation
        if not relation.evaluate(eval_value, eval_other_value):
            rel = relation.user_friendly_relation(eval_value, eval_other_value)
            first_loc = (eval_value[0], input_info.location.user_repr())
            second_loc = (eval_other_value[0], rel_input_info.location.user_repr())
            rel_str = relation.user_friendly_relation(first_loc, second_loc)
            message = self.create_relation_error(rel_str, rel)
            error.error_message = message
            return error
        return None

    def rel_error(self, input_id, other_id, val, rel_info, relation, loc, assmp, in_val):
        """Creates a relational error

        :param input_id: input id of the first input
        :param other_id: input id of the second input
        :param val: value of the first input
        :param rel_info: information about the second input
        :param relation: relation that is violated
        :param loc: location of the input
        :param assmp: assumption of the input
        :param in_val: input line of the input
        :return: ErrorInformation object that includes all needed information
        """
        inverted = input_id.input_id > other_id.input_id
        val1 = (input_id, val)
        val2 = (other_id, rel_info.eval_value)
        if not inverted:
            rel_eval = relation.user_friendly_relation(val1, val2)
        else:
            rel_eval = relation.user_friendly_relation(val2, val1)
        first_loc = (input_id, loc.user_repr())
        second_loc = (other_id, rel_info.location.user_repr())
        if not inverted:
            rel_str = relation.user_friendly_relation(first_loc, second_loc)
        else:
            rel_str = relation.user_friendly_relation(second_loc, first_loc)
        msg = self.write_relation_error(rel_str, rel_eval)
        lvl = ErrorInformation.ErrorLevel.Relation
        input_info = InputInfo(in_val, loc, assmp, self.prev_line)
        if not inverted:
            new_error = ErrorInformation(input_info, msg, lvl)
            new_error.add_rel_info(relation, rel_info)
        else:
            new_error = ErrorInformation(rel_info, msg, lvl)
            new_error.add_rel_info(relation, input_info)
        if isinstance(relation.this_id, CheckerZeroIdentifier):
            new_error.is_first_val = False
        return new_error

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
            loc = error.infos1.location
            new_val = error.infos1.orig_value
            error.error_level = error_level
            if error_level == ErrorInformation.ErrorLevel.Type:
                message = self.create_type_error(loc, new_val, type_assmp)
            else:
                message = self.create_range_error(loc, new_val, range_assmp)
            error.error_message = message
            return error_level

        return val
