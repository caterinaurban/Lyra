import json
from json import JSONDecoder
from typing import Set

from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, TypeLattice
from lyra.abstract_domains.quality.simple_relation_lattice import SimpleExpression
from lyra.core.expressions import VariableIdentifier
from lyra.quality_analysis.input_assmp_simplification import CheckerRelation, \
    CheckerAssumption, CheckerMultiAssumption, CheckerExpression


class IdJSON:
    """Constants for the JSON encoding."""
    type_assmp = "type_assmp"
    iterations = "iterations"
    assmps = "assmps"
    relations = "relations"
    inputs = "inputs"
    id = "id"
    rel_this_pos = "rel_this_pos"
    rel_this_id = "rel_this_id"
    rel_constant = "rel_constant"
    rel_other_pos = "rel_other_pos"
    rel_other_id = "rel_other_id"
    expr_var_pos = "expr_var_pos"
    expr_var = "expr_var"
    expr_const = "expr_const"


class AssumptionEncoder(json.JSONEncoder):
    """Converter from input assumptions to serializable objects."""
    def default(self, obj):
        """ Turns the assumption objects into serializable objects

        :param obj: current object to turn into a serializable object
        :return: serializable object representation of the assumption objects
        """
        if isinstance(obj, CheckerMultiAssumption):
            return {IdJSON.iterations: obj.iterations, IdJSON.assmps: obj.assmps}
        if isinstance(obj, CheckerAssumption):
            return {IdJSON.type_assmp: obj.assmps.type_assumption, IdJSON.relations: obj.relations,
                    IdJSON.id: obj.var_id}
        if isinstance(obj, CheckerRelation):
            return {IdJSON.rel_this_pos: obj.this_pos, IdJSON.rel_this_id: obj.this_id,
                    IdJSON.rel_other_pos: obj.other_pos, IdJSON.rel_other_id: obj.other_id,
                    IdJSON.rel_constant: obj.constant}
        if isinstance(obj, SimpleExpression):
            return {IdJSON.expr_var_pos: obj.var_pos, IdJSON.expr_var: obj.var,
                    IdJSON.expr_const: obj.const}
        if isinstance(obj, VariableIdentifier):
            return obj.name
        if isinstance(obj, TypeLattice):
            return obj.__repr__()
        if isinstance(obj, Set):
            return {IdJSON.inputs: list(obj)}
        return json.JSONEncoder.default(self, obj)


class AssumptionDecoder(json.JSONDecoder):
    """Converter from serialized objects to input assumptions."""
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.default)

    def default(self, obj):
        """ Turns the serialized objects back to assumptions

        :param obj: current serialized object
        :return: assumption representation of the serialized objects
        """

        if IdJSON.rel_this_pos in obj:
            this_pos = obj[IdJSON.rel_this_pos]
            this_id = obj[IdJSON.rel_this_id]
            constant = obj[IdJSON.rel_constant]
            other_pos = obj[IdJSON.rel_other_pos]
            other_id = obj[IdJSON.rel_other_id]
            return CheckerRelation(this_pos, this_id, other_pos, other_id, constant)

        if IdJSON.id in obj:
            type_assmp = obj[IdJSON.type_assmp]
            type_assumption = TypeLattice()
            if type_assmp == "Int":
                type_assumption = TypeLattice().integer()
            elif type_assmp == "Float":
                type_assumption = TypeLattice().real()
            assmp = AssumptionLattice(type_assumption)
            return CheckerAssumption(obj[IdJSON.id], assmp, obj[IdJSON.relations])

        if IdJSON.iterations in obj:
            num_iter = obj[IdJSON.iterations]
            assmps = obj[IdJSON.assmps]
            return CheckerMultiAssumption(num_iter, assmps)

        if IdJSON.expr_var in obj:
            var_pos = obj[IdJSON.expr_var_pos]
            var = obj[IdJSON.expr_var]
            if var == ".VAR0":
                var = None
            const = obj[IdJSON.expr_const]
            return CheckerExpression(var_pos, var, const)

        if IdJSON.inputs in obj:
            return obj[IdJSON.inputs]

        raise NotImplementedError(f"JSON Decoding for object {obj} is not implemented.")


class JSONHandler:
    """
    Handles methods to create and read json files created by an assumption analysis to use them
    for the input checker.
    """
    def __init__(self, program_path, program_name):
        self.filename = f"{program_path}{program_name}.json"

    def input_assumptions_to_json(self, checker_assumptions, inputs: Set[str]):
        """Writes the assumptions to a json file.

        :param checker_assumptions: the assumptions that are written to a json file
        :param inputs: set of inputs the checker needs to store for relation checking
        """
        with open(self.filename, 'w') as f:
            json.dump([checker_assumptions, inputs], f, cls=AssumptionEncoder, indent=4)

    def json_to_input_assumptions(self):
        """Reads assumptions from a json file."""
        try:
            with open(self.filename, 'r') as f:
                data, inputs = json.load(f, cls=AssumptionDecoder)
            return data, inputs
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.filename} does not exist.")
