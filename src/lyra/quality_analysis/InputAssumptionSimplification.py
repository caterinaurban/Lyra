from math import inf

from lyra.abstract_domains.numerical.interval_domain import IntervalLattice
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, \
    MultiInputAssumptionLattice
from lyra.engine.result import AnalysisResult


class SimpleRelation:
    """Stores relational constraints."""

    def __init__(self, this_pos: bool, constant: int, other_pos: bool, other_id):
        self.this_pos = this_pos
        self.constant = constant
        self.other_pos = other_pos
        self.other_id = other_id

    def evaluate(self, this_value: float, other_value=None) -> bool:
        """Evaluates the relation with the given values.

        :param this_value: value for THIS variable
        :param other_value: value for the other variable if existing
        :return: if the evaluated relation is true
        """
        assert (self.other_id is None) == (other_value is None)
        curr_val = this_value if self.this_pos else -this_value
        curr_val += self.constant
        if other_value is not None:
            if self.other_pos:
                curr_val += other_value
            else:
                curr_val -= other_value
        return curr_val <= 0

    def create_user_friendly_message(self) -> str:
        """Create a user friendly string of the current relation

        :return: A user friendly message of the current relation
        """
        if self.this_pos:
            if self.other_id is not None:
                error = "User friendly creation with other variable is not implemented yet."
                raise NotImplementedError(error)
            else:
                return f"THIS <= {-self.constant}"
        else:
            if self.other_id is not None:
                error = "User friendly creation with other variable is not implemented yet."
                raise NotImplementedError(error)
            else:
                return f"THIS >= {-self.constant}"

    def __repr__(self):
        sign_this = "" if self.this_pos else "-"
        repr_str = f"{sign_this}THIS"
        if self.other_id is not None:
            sign_other = "" if self.other_pos else "-"
            repr_str += f" {sign_other} id:{self.other_id}"
        if self.constant != 0:
            sign_constant = "" if self.constant > 0 else "-"
            constant = self.constant if self.constant > 0 else -self.constant
            repr_str += f" {sign_constant} {constant}"
        return f"{repr_str} <= 0"


class SimpleAssumption:
    """Stores assumptions in a simple way for the JSON encoding."""
    def __init__(self, var_id: int, assmps: AssumptionLattice, relations: [SimpleRelation]):
        self.var_id = var_id
        self.assmps = assmps
        self.relations = relations

    def __repr__(self):
        return f"({self.var_id}, {self.assmps}, {self.relations})"


class InputAssumptionSimplification:

    def analysis_result_to_simple_assmps(self, result: AnalysisResult) -> [SimpleAssumption]:
        """Turns an analysis result into a list of SimpleAssumptions.

        :param result: Result of the analysis
        :return: a list of SimpleAssumptions
        """
        for node, items in result.result.items():
            if node.identifier == 1:
                return self.result_to_input_assmps(items[0].stack_top.assmps)
        raise Exception("Initial result could not be found.")

    def result_to_input_assmps(self, assmps) -> [SimpleAssumption]:
        """Turns assumption of an analysis result into a list of SimpleAssumptions

        :param assmps: assumptions of an analysis result
        :return: a list of SimpleAssumptions
        """
        new_assmps = []
        for assmp in assmps:
            if isinstance(assmp, MultiInputAssumptionLattice):
                inner_assmps = self.result_to_input_assmps(assmp.assmps)
                assmp.assmps.clear()
                assmp.assmps.extend(inner_assmps)
                new_assmps.append(assmp)
            else:
                var_id = assmp.input_info[assmp.var_name]
                relations = []
                if assmp.var_name in assmp.relations.store:
                    relation = assmp.relations.store[assmp.var_name]
                    relations = self.lattice_to_simple_relations(relation)
                assumption = SimpleAssumption(var_id, assmp.assmp, relations)
                new_assmps.append(assumption)
        return new_assmps

    def lattice_to_simple_relations(self, lattice: IntervalLattice) -> [SimpleRelation]:
        """ Turns relations into SimpleRelation objects.

        :param lattice: lattice element to turn into SimpleRelation objects
        :return: a list of created SimpleRelation objects
        """
        relations = []
        if lattice.lower != -inf:
            relations.append(SimpleRelation(False, lattice.lower, True, None))
        if lattice.upper != inf:
            relations.append(SimpleRelation(True, -lattice.upper, True, None))
        return relations
