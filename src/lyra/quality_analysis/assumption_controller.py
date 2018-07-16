import glob
import os

from lyra.abstract_domains.assumption.octagons_domain import OctagonState
from lyra.abstract_domains.quality.character_inclusion_domain import CharacterInclusionState
from lyra.quality.controller import Controller
from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.input_checker import InputChecker
from lyra.quality_analysis.json_handler import JSONHandler


class AssumptionController(Controller):

    def __init__(self, analysis_runner: 'AssumptionAnalysis', checker: 'InputChecker', result_handler: 'JSONHandler', canonical_path: str, numerical_domain: 'State', string_domain: 'State', code_modified=True, input_file_path=None):
        super().__init__(analysis_runner, checker, result_handler, canonical_path, numerical_domain, string_domain, code_modified, input_file_path)
        print("Initialized assumption controller.")


if __name__ == "__main__":
    name = os.getcwd() + '/example/**.py'
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            AssumptionController(AssumptionAnalysis(), InputChecker(), JSONHandler(), path, OctagonState, CharacterInclusionState).run()
