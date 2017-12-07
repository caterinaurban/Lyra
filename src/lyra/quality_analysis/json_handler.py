import json
from json import JSONDecoder

from lyra.abstract_domains.numerical.interval_domain import IntervalLattice
from lyra.abstract_domains.quality.assumption_lattice import AssumptionLattice, TypeLattice


class AssumptionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AssumptionLattice):
            return {"assmp":obj.type_assumption, "range":obj.range_assumption}
        if isinstance(obj, TypeLattice):
            return obj.__repr__()
        if isinstance(obj, IntervalLattice):
            return obj.__repr__()

        return json.JSONEncoder.default(self, obj)


class AssumptionDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        JSONDecoder.__init__(self, object_hook=self.default, *args, **kargs)

    def default(self, obj):

        return obj  #TODO


class JSONHandler:
    """
    Handles methods to create and read json files created by an assumption analysis to use them
    for the input checker
    """

    def filename(self, program_name):
        return f'assumptions_{program_name}.json'

    def input_assumptions_to_json(self, program_name, final_input_state):
        """
        Writes the assumptions to a json file
        """
        final_input_dict = {"0":final_input_state}
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
            raise error
