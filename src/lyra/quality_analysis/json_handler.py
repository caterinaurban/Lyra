import json
from json import JSONDecoder
from math import inf

from lyra.abstract_domains.numerical.interval_domain import IntervalLattice
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, TypeLattice, \
    InputAssumptionLattice


class AssumptionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, InputAssumptionLattice):
            return {"iterations": obj.iterations, "assmps": obj.assmps}
        if isinstance(obj, AssumptionLattice):
            return {"type_assmp": obj.type_assumption, "range_assmp": obj.range_assumption}
        if isinstance(obj, TypeLattice):
            return obj.__repr__()
        if isinstance(obj, IntervalLattice):
            return obj.__repr__()

        return json.JSONEncoder.default(self, obj)


class AssumptionDecoder(json.JSONDecoder):

    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.default)

    def default(self, obj):

        if "0" in obj:
            return obj["0"]

        if "iterations" in obj:
            num_iter = obj["iterations"]
            assmps = obj["assmps"]
            return InputAssumptionLattice(num_iter, assmps)

        type_assumption = TypeLattice()
        range_assumption = IntervalLattice()
        if "type_assmp" in obj:
            type_assmp = obj["type_assmp"]
            if type_assmp == "Int":
                type_assumption = TypeLattice().integer()
            elif type_assmp == "Float":
                type_assumption = TypeLattice().real()
        if "range_assmp" in obj:
            bounds = obj["range_assmp"]
            if bounds == '⊥':
                range_assumption = IntervalLattice().bottom()
            elif bounds == 'T':
                range_assumption = IntervalLattice()
            else:
                bounds = obj["range_assmp"][1:-1].split(',')
                bounds[0] = -inf if bounds[0].strip() == "-inf" else int(bounds[0])
                bounds[1] = inf if bounds[1].strip() == "inf" else int(bounds[1])
                range_assumption = IntervalLattice(bounds[0], bounds[1])

        return AssumptionLattice(type_assumption, range_assumption)


class JSONHandler:
    """
    Handles methods to create and read json files created by an assumption analysis to use them
    for the input checker
    """

    def filename(self, program_name):
        return f'{program_name}.json'

    def input_assumptions_to_json(self, program_name, final_input_state):
        """
        Writes the assumptions to a json file
        """
        final_input_dict = {"0": final_input_state}
        with open(self.filename(program_name), 'w') as f:
            json.dump(final_input_dict, f, cls=AssumptionEncoder, indent=4)

    def json_to_input_assumptions(self, program_name):
        """
        Reads assumptions from a json file
        """
        try:
            with open(self.filename(program_name), 'r') as f:
                data = json.load(f, cls=AssumptionDecoder)
            return data
        except FileNotFoundError:
            error = f'No file with name {self.filename(program_name)} was found ' \
                    f'for program {program_name}'
            raise FileNotFoundError(error)
