from typing import Set

from lyra.abstract_domains.quality.assumption_lattice import MultiInputAssumptionLattice
from lyra.abstract_domains.quality.simple_relation_lattice import SimpleRelation, SimpleExpression
from lyra.core.expressions import VariableIdentifier
from lyra.engine.result import AnalysisResult


class CheckerRelation:
    """Representation of a relation suitable for input checking.

    Format: +/- THIS_VAR +/- OTHER_VAR + CONSTANT
    """
    def __init__(self, this_pos: bool, this_id: str, other_pos: bool, other_id: str, constant):
        self.this_pos = this_pos
        self.this_id = this_id
        self.other_pos = other_pos
        self.other_id = other_id
        self.constant = constant

    def evaluate(self, this_value, other_value) -> bool:
        """Evaluates the relation with the given values.

        :param this_value: value for THIS variable
        :param other_value: value for the other variable if existing
        :return: if the evaluated relation is true
        """
        curr_val = this_value if self.this_pos else -this_value
        curr_val += self.constant
        if other_value is not None:
            if self.other_pos:
                curr_val += other_value
            else:
                curr_val -= other_value
        return curr_val <= 0

    def user_friendly_relation_with_vars(self) -> str:
        """Creates a user friendly representation of the relation using the input ids

        :return: a user friendly representation of the relation using the input ids
        """
        return self.user_friendly_relation(self.this_id, self.other_id)

    def user_friendly_relation(self, this_val, other_val) -> str:
        """Creates a user friendly representation of the relation

        :param this_val: the value that is substituted with the first variable
        :param other_val: the value that is substituted with the second variable
        :return: a user friendly representation of the relation
        """
        if self.other_id is None:
            if self.this_pos:
                return f"{this_val} <= {-self.constant}"
            else:
                return f"{this_val} <= {self.constant}"
        if self.this_pos and self.other_pos:
            return f"{this_val} + {other_val} <= {-self.constant}"
        elif self.this_pos:
            sign_const = "-" if self.constant > 0 else "+"
            constant = self.constant if self.constant >= 0 else -self.constant
            return f"{this_val} <= {other_val} {sign_const} {constant}"
        elif self.other_pos:
            sign_const = "-" if self.constant < 0 else "+"
            constant = self.constant if self.constant >= 0 else -self.constant
            return f"{this_val} >= {other_val} {sign_const} {constant}"
        else:
            return f"{this_val} + {other_val} >= {-self.constant}"

    def __repr__(self):
        sign_this = "" if self.this_pos else "-"
        sign_other = "+" if self.other_pos else "-"
        sign_constant = "+" if self.constant >= 0 else "-"
        constant = self.constant
        if self.constant < 0:
            constant = -constant
        left = f"{sign_this}{self.this_id} {sign_other} {self.other_id} {sign_constant} {constant}"
        return f"{left} <= 0"


class CheckerAssumption:
    """Stores assumptions in a simple way for the JSON encoding and the input checker."""
    def __init__(self, var_id: str, assmps, relations: [CheckerRelation]):
        self.var_id = var_id
        self.assmps = assmps
        self.relations = relations

    def __repr__(self):
        var_id = self.var_id.split("=")[1]
        if len(self.relations) == 0:
            return f"{var_id}:{self.assmps}"
        return f"{var_id}:({self.assmps}, {self.relations})"


class CheckerMultiAssumption:
    """Stores assumptions that hold for a number of times in a simple way for the JSON encoding
    and the input checker."""
    def __init__(self, iterations: SimpleExpression, assmps):
        self.iterations = iterations
        self.assmps = assmps

    def __repr__(self):
        return f"{self.iterations} x {self.assmps}"


class CheckerExpression:
    """Stores a simple expression"""
    def __init__(self, var_pos, var, const: float = 0):
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
        value = var_to_val[self.var] + self.const
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


class InputAssumptionSimplification:
    """Performs a simplification of the analysis result."""
    def analysis_result_to_checker_assmps(self, result: AnalysisResult):
        """Turns an analysis result into a list of Checker(Multi)Assumptions.

        :param result: Result of the analysis
        :return: a list of Checker(Multi)Assumptions
        """
        for node, items in result.result.items():
            if node.identifier == 1:
                checker_assmps = self.result_to_checker_assmps(items[0].stack_top.assmps)
                inputs = self.extract_inputs(checker_assmps)
                return checker_assmps, inputs
        raise Exception("Initial result could not be found.")

    def result_to_checker_assmps(self, assmps):
        """Turns assumptions of an analysis result into a list of Checker(Multi)Assumptions

        :param assmps: assumptions of an analysis result
        :return: a list of Checker(Multi)Assumptions
        """
        checker_assmps = []
        for assmp in assmps:
            if isinstance(assmp, MultiInputAssumptionLattice):
                iterations = assmp.iterations
                inner_assmps = self.result_to_checker_assmps(assmp.assmps)
                checker_assmps.append(CheckerMultiAssumption(iterations, inner_assmps))
            else:
                var_id = assmp.input_id
                checker_relations = []
                for relation in assmp.relations.relations:
                    checker_relations.append(self.to_checker_relation(relation, var_id))
                assumption = CheckerAssumption(var_id.name, assmp.assmp, checker_relations)
                checker_assmps.append(assumption)
        return checker_assmps

    def to_checker_relation(self, relation: SimpleRelation, var_id: VariableIdentifier):
        """Turns a SimpleRelation into a CheckerRelation

        :param relation: relation to turn into a CheckerRelation
        :param var_id: input id the relation belongs to
        :return: a newly created CheckerRelation
        """
        if relation.first == var_id:
            this_pos = relation.first_pos
            this_id = relation.first.name
            other_pos = relation.second_pos
            other_id = relation.second
        elif relation.second == var_id:
            this_pos = relation.second_pos
            this_id = relation.second.name
            other_pos = relation.first_pos
            other_id = relation.first
        else:
            error = f"Relation {relation} does not include the input id {var_id}."
            raise EnvironmentError(error)
        constant = relation.constant
        return CheckerRelation(this_pos, this_id, other_pos, other_id, constant)

    def extract_inputs(self, assumptions) -> Set[str]:
        """Extracts all inputs from relations that are needed for the input checker to store

        :param assumptions: assumptions to extract the inputs from
        :return: set of all inputs
        """
        inputs = set()
        for assmp in assumptions:
            if isinstance(assmp, CheckerMultiAssumption):
                inputs.add(assmp.iterations.var.name)
                inputs.union(self.extract_inputs(assmp.assmps))
            else:
                for relation in assmp.relations:
                    inputs.add(relation.other_id.name)
        return inputs
