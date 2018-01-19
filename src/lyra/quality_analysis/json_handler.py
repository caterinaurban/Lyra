import json
from json import JSONDecoder

from lyra.abstract_domains.numerical.interval_domain import IntervalState
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, TypeLattice, \
    InputAssumptionLattice, MultiInputAssumptionLattice
from lyra.quality_analysis.InputAssumptionSimplification import SimpleRelation, SimpleAssumption


class IdJSON:
    """Constants for the JSON encoding."""
    type_assmp = "type_assmp"
    iterations = "iterations"
    assmps = "assmps"
    relations = "relations"
    id = "id"
    rel_this_pos = "rel_this_pos"
    rel_constant = "rel_constant"
    rel_other_pos = "rel_other_pos"
    rel_other_id = "rel_other_id"


class AssumptionEncoder(json.JSONEncoder):
    """Converter from input assumptions to serializable objects."""
    def default(self, obj):
        """ Turns the assumption objects into serializable objects

        :param obj: current object to turn into a serializable object
        :return: serializable object representation of the assumption objects
        """
        if isinstance(obj, MultiInputAssumptionLattice):
            if isinstance(obj.iterations, InputAssumptionLattice):
                raise NotImplementedError
            else:
                return {IdJSON.iterations: obj.iterations, IdJSON.assmps: obj.assmps}
        if isinstance(obj, SimpleAssumption):
            return {IdJSON.type_assmp: obj.assmps.type_assumption, IdJSON.relations: obj.relations,
                    IdJSON.id: obj.var_id}
        if isinstance(obj, TypeLattice):
            return obj.__repr__()
        if isinstance(obj, SimpleRelation):
            return {IdJSON.rel_this_pos: obj.this_pos, IdJSON.rel_other_pos: obj.other_pos,
                    IdJSON.rel_other_id: obj.other_id, IdJSON.rel_constant: obj.constant}
        if isinstance(obj, IntervalState):
            raise NotImplementedError
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
            constant = obj[IdJSON.rel_constant]
            other_pos = obj[IdJSON.rel_other_pos]
            other_id = obj[IdJSON.rel_other_id]
            return SimpleRelation(this_pos, constant, other_pos, other_id)

        if IdJSON.id in obj:
            type_assmp = obj[IdJSON.type_assmp]
            type_assumption = TypeLattice()
            if type_assmp == "Int":
                type_assumption = TypeLattice().integer()
            elif type_assmp == "Float":
                type_assumption = TypeLattice().real()
            assmp = AssumptionLattice(type_assumption)
            return SimpleAssumption(obj[IdJSON.id], assmp, obj[IdJSON.relations])

        if "iterations" in obj:
            num_iter = obj[IdJSON.iterations]
            assmps = obj[IdJSON.assmps]
            return MultiInputAssumptionLattice(num_iter, assmps)

        raise NotImplementedError(f"JSON Decoding for object {obj} is not implemented.")


class JSONHandler:
    """
    Handles methods to create and read json files created by an assumption analysis to use them
    for the input checker.
    """
    def __init__(self, program_path, program_name):
        self.filename = f"{program_path}{program_name}.json"

    def input_assumptions_to_json(self, final_input_state):
        """Writes the assumptions to a json file."""
        final_input_dict = final_input_state
        with open(self.filename, 'w') as f:
            json.dump(final_input_dict, f, cls=AssumptionEncoder, indent=4)

    def json_to_input_assumptions(self):
        """Reads assumptions from a json file."""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f, cls=AssumptionDecoder)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.filename} does not exist.")
