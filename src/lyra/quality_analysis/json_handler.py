import json
from json import JSONDecoder
from typing import Set

from lyra.abstract_domains.numerical.interval_domain import IntervalLattice
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, TypeLattice, \
    InputAssumptionLattice, MultiInputAssumptionLattice
from lyra.abstract_domains.quality.simple_relation_lattice import SimpleExpression, \
    SimpleRelationsLattice, SimpleRelation
from lyra.core.expressions import VariableIdentifier, LengthIdentifier
from lyra.quality_analysis.input_assmp_simplification import CheckerRelation, \
    CheckerAssumption, CheckerMultiAssumption, CheckerExpression, CheckerLengthIdentifier, \
    CheckerIdentifier, CheckerZeroIdentifier


class IdJSON:
    """Constants for the JSON encoding."""
    type_assmp = "type_assmp"
    range_assmp = "range_assmp"
    iterations = "iterations"
    assmps = "assmps"
    delimiter = "delimiter"
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
        if isinstance(obj, MultiInputAssumptionLattice):
            return {IdJSON.iterations: obj.iterations, IdJSON.assmps: obj.assmps,
                    IdJSON.delimiter: obj.delimiter}
        if isinstance(obj, InputAssumptionLattice):
            return {IdJSON.type_assmp: obj.assmp.type_assumption,
                    IdJSON.range_assmp: obj.assmp.range_assumption,
                    IdJSON.relations: obj.relations, IdJSON.id: obj.input_id}
        if isinstance(obj, SimpleRelationsLattice):
            return [r for r in obj.relations]
        if isinstance(obj, SimpleRelation):
            return {IdJSON.rel_this_pos: obj.first_pos, IdJSON.rel_this_id: obj.first,
                    IdJSON.rel_other_pos: obj.second_pos, IdJSON.rel_other_id: obj.second,
                    IdJSON.rel_constant: obj.constant}
        if isinstance(obj, SimpleExpression):
            return {IdJSON.expr_var_pos: obj.var_pos, IdJSON.expr_var: obj.var,
                    IdJSON.expr_const: obj.const}
        if isinstance(obj, (VariableIdentifier, LengthIdentifier)):
            return obj.name
        if isinstance(obj, TypeLattice):
            return obj.__repr__()
        if isinstance(obj, IntervalLattice):
            return [obj.lower, obj.upper]
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
            id1 = self.convert_to_identifier(obj[IdJSON.rel_this_id])
            id2 = self.convert_to_identifier(obj[IdJSON.rel_other_id])
            if isinstance(id1, CheckerZeroIdentifier):
                this_pos = obj[IdJSON.rel_other_pos]
                this_id = id2
                other_pos = obj[IdJSON.rel_this_pos]
                other_id = id1
            else:
                this_pos = obj[IdJSON.rel_this_pos]
                this_id = id1
                other_pos = obj[IdJSON.rel_other_pos]
                other_id = id2
            constant = obj[IdJSON.rel_constant]
            return CheckerRelation(this_pos, this_id, other_pos, other_id, constant)

        if IdJSON.id in obj:
            type_assmp = obj[IdJSON.type_assmp]
            type_assumption = TypeLattice()
            if type_assmp == "Int":
                type_assumption = TypeLattice().integer()
            elif type_assmp == "Float":
                type_assumption = TypeLattice().real()
            range_assmp = obj[IdJSON.range_assmp]
            range_assumption = IntervalLattice(range_assmp[0], range_assmp[1])
            assmp = AssumptionLattice(type_assumption, range_assumption)
            input_id = self.convert_to_identifier(obj[IdJSON.id])
            return CheckerAssumption(input_id, assmp, obj[IdJSON.relations])

        if IdJSON.iterations in obj:
            num_iter = obj[IdJSON.iterations]
            assmps = obj[IdJSON.assmps]
            delimiter = obj[IdJSON.delimiter]
            return CheckerMultiAssumption(num_iter, assmps, delimiter)

        if IdJSON.expr_var in obj:
            var_pos = obj[IdJSON.expr_var_pos]
            var = self.convert_to_identifier(obj[IdJSON.expr_var])
            const = obj[IdJSON.expr_const]
            return CheckerExpression(var_pos, var, const)

        if IdJSON.inputs in obj:
            input_ids = [self.convert_to_identifier(inp) for inp in obj[IdJSON.inputs]]
            return [inp for inp in input_ids if inp is not None]

        raise NotImplementedError(f"JSON Decoding for object {obj} is not implemented.")

    def convert_to_identifier(self, input_name: str):
        """Converts an input id to an input identifier object

        :param input_name: name of the input to convert
        :return: the newly created identifier
        """
        if input_name.startswith("len("):
            input_id = input_name.split("=")[1][:-1]
            return CheckerLengthIdentifier(int(input_id))
        elif input_name == ".VAR0":
            return CheckerZeroIdentifier()
        input_id = input_name.split("=")[1]
        return CheckerIdentifier(int(input_id))


class JSONHandler:
    """
    Handles methods to create and read json files created by an assumption analysis to use them
    for the input checker.
    """
    def __init__(self, program_path, program_name):
        self.filename = f"{program_path}{program_name}.json"

    def input_assumptions_to_json(self, input_assmps, inputs: Set[str]):
        """Writes the assumptions to a json file.

        :param input_assmps: the assumptions that are written to a json file
        :param inputs: set of inputs the checker needs to store for relation checking
        """
        with open(self.filename, 'w') as f:
            json.dump([input_assmps, inputs], f, cls=AssumptionEncoder, indent=4)

    def json_to_input_assumptions(self):
        """Reads assumptions from a json file."""
        try:
            with open(self.filename, 'r') as f:
                data, inputs = json.load(f, cls=AssumptionDecoder)
            return data, inputs
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.filename} does not exist.")
