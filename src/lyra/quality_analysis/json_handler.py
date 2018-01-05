import json
from json import JSONDecoder
from math import inf

from lyra.abstract_domains.numerical.interval_domain import IntervalLattice
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, TypeLattice, \
    InputAssumptionLattice


class AssumptionEncoder(json.JSONEncoder):
    """Converter from input assumptions to serializable objects."""
    def default(self, obj):
        """ Turns the assumption objects into serializable objects

        :param obj: current object to turn into a serializable object
        :return: serializable object representation of the assumption objects
        """
        if isinstance(obj, InputAssumptionLattice):
            if obj.iterations is None:
                return {}
            return {"iterations": obj.iterations, "assmps": obj.assmps}
        if isinstance(obj, AssumptionLattice):
            return {"type_assmp": obj.type_assumption, "range_assmp": obj.range_assumption}
        if isinstance(obj, TypeLattice):
            return obj.__repr__()
        if isinstance(obj, IntervalLattice):
            return obj.__repr__()
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
        if not obj:
            return None

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
    for the input checker.
    """
    def __init__(self, program_path, program_name):
        self.filename = f"{program_path}{program_name}.json"

    def input_assumptions_to_json(self, final_input_state):
        """Writes the assumptions to a json file."""
        final_input_dict = {"0": final_input_state}
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
