class CheckerIdentifier:
    """Representation of an input identifier."""
    def __init__(self, input_id: int, identifier: str=None):
        self.input_id = input_id
        self.identifier = identifier if identifier is not None else f".ID={input_id}"

    def __hash__(self):
        return hash((self.identifier, self.input_id))

    def __eq__(self, other):
        return self.identifier == other.identifier and self.input_id == other.input_id

    def __repr__(self):
        return f"{self.identifier}"

    def __str__(self):
        return f"{self.identifier}"


class CheckerLengthIdentifier(CheckerIdentifier):
    """Representation of an input identifier that represents the length of an input."""
    def __init__(self, input_id: int):
        super().__init__(input_id, f"len(.ID={input_id})")


class CheckerZeroIdentifier(CheckerIdentifier):
    """Representation of an input identifier that represents the value 0."""
    def __init__(self):
        super().__init__(-1, f".VAR0")


class CheckerRelation:
    """Representation of a relation suitable for input checking.

    Format: +/- THIS_VAR +/- OTHER_VAR + CONSTANT
    """
    def __init__(self, this_pos: bool, this_id, other_pos: bool, other_id, constant):
        self.this_pos = this_pos
        self.this_id = this_id
        self.other_pos = other_pos
        self.other_id = other_id
        self.constant = constant

    def evaluate(self, value, value2) -> bool:
        """Evaluates the relation given two values with format (input id, value)

        :param value: (input id, value) of one value
        :param value2: (input id, value) of other value
        :return: True if the relation is correct
        """
        if value[0] == self.this_id and value2[0] == self.other_id:
            this_value = value[1]
            other_value = value2[1]
        elif value[0] == self.other_id and value2[0] == self.this_id:
            this_value = value2[1]
            other_value = value[1]
        else:
            error = f"{value} and {value2} are not compatible with relation {self}"
            raise Exception(error)
        curr_val = this_value if self.this_pos else -this_value
        curr_val += self.constant
        curr_val += other_value if self.other_pos else -other_value
        return curr_val <= 0

    def get_other_id(self, input_id: CheckerIdentifier):
        """Given an input id this method returns the other id used in this relation

        :param input_id: input id whose relation partner should be found
        :return: input id of the other relation partner
        """
        if self.this_id is not None and self.this_id == input_id:
            return self.other_id
        if self.other_id is not None and self.other_id == input_id:
            return self.this_id
        if self.this_id is not None and isinstance(self.this_id, CheckerLengthIdentifier):
            if self.this_id.input_id == input_id:
                return self.other_id
        if self.other_id is not None and isinstance(self.other_id, CheckerLengthIdentifier):
            if self.other_id.input_id == input_id:
                return self.this_id
        return None

    def user_friendly_relation(self, first_value, second_value) -> str:
        """Creates a user friendly representation of the relation

        :param first_value: (input id, value) that is substituted with one variable
        :param second_value: (input id, value) that is substituted with the other variable
        :return: a user friendly representation of the relation
        """
        if first_value[0] == self.this_id and second_value[0] == self.other_id:
            this_val = first_value[1]
            other_val = second_value[1]
        elif first_value[0] == self.other_id and second_value[0] == self.this_id:
            this_val = second_value[1]
            other_val = first_value[1]
        else:
            error = f"{first_value} and {second_value} are not compatible with relation {self}"
            raise Exception(error)
        if isinstance(this_val, CheckerZeroIdentifier):
            this_val = 0
        if isinstance(other_val, CheckerZeroIdentifier):
            other_val = 0
        if self.other_id is None:
            if self.this_pos:
                return f"{this_val} ≤ {-self.constant}"
            else:
                return f"{this_val} ≤ {self.constant}"
        if self.this_pos and self.other_pos:
            return f"{this_val} + {other_val} ≤ {-self.constant}"
        elif self.this_pos:
            sign_const = "-" if self.constant > 0 else "+"
            constant = self.constant if self.constant >= 0 else -self.constant
            return f"{this_val} ≤ {other_val} {sign_const} {constant}"
        elif self.other_pos:
            sign_const = "-" if self.constant < 0 else "+"
            constant = self.constant if self.constant >= 0 else -self.constant
            return f"{this_val} ≥ {other_val} {sign_const} {constant}"
        else:
            return f"{this_val} + {other_val} ≥ {-self.constant}"

    def __repr__(self):
        sign_this = "" if self.this_pos else "-"
        sign_other = "+" if self.other_pos else "-"
        sign_constant = "+" if self.constant >= 0 else "-"
        constant = self.constant
        if self.constant < 0:
            constant = -constant
        left = f"{sign_this}{self.this_id} {sign_other} {self.other_id} {sign_constant} {constant}"
        return f"{left} ≤ 0"


class CheckerAssumption:
    """Stores assumptions in a simple way for the JSON encoding and the input checker."""
    def __init__(self, var_id: CheckerIdentifier, assmp, relations: [CheckerRelation]):
        self.var_id = var_id
        self.assmp = assmp
        self.relations = relations

    def __repr__(self):
        var_id = self.var_id.input_id
        if len(self.relations) == 0:
            return f"{var_id}:{self.assmp}"
        return f"{var_id}:({self.assmp}, {self.relations})"


class CheckerMultiAssumption:
    """Stores assumptions that hold for a number of times in a simple way for the JSON encoding
    and the input checker."""
    def __init__(self, iterations: 'CheckerExpression', assmps, delimiter: str):
        self.iterations = iterations
        self.assmps = assmps
        self.delimiter = delimiter

    def __repr__(self):
        delimiter = f" with delimiter \'{self.delimiter}\'" if self.delimiter is not None else ""
        return f"{self.iterations} x {self.assmps}{delimiter}"


class CheckerExpression:
    """Stores a simple expression"""
    def __init__(self, var_pos, var, const):
        super().__init__()
        self.var_pos = var_pos
        self.var = var
        self.const = const

    def evaluate(self, var_to_val: dict):
        """Evaluates the expression given a dictionary of variables to values

        :param var_to_val: map from variables to values
        :return: evaluated value if possible, else None
        """
        if self.var is None:
            return self.const
        if self.var not in var_to_val or var_to_val[self.var] is None:
            return None
        value = var_to_val[self.var].eval_value + self.const
        if not self.var_pos:
            value = -value
        return value

    def __repr__(self):
        if self.var is None:
            return f"{self.const.__repr__()}"
        var_sign = "" if self.var_pos else "-"
        if self.const < 0:
            return f"({var_sign}{self.var} - {-self.const})"
        return f"({var_sign}{self.var} + {self.const})"
