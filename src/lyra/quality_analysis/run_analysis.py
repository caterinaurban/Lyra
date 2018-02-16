from lyra.abstract_domains.quality.assumption_lattice import MultiInputAssumptionLattice
from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.input_checker import InputChecker, ErrorInformation
from lyra.quality_analysis.json_handler import JSONHandler


class QualityAnalysisRunner:

    def __init__(self, program_path, program_name, input_file_name):
        self.program_path = program_path
        self.program_name = program_name
        self.analysis = AssumptionAnalysis(False)
        self.json_handler = JSONHandler(program_path, program_name)
        self.input_checker = InputChecker(program_path, input_file_name, program_name)

    def run_analysis(self):
        """Runs the quality analysis."""
        print("Running analysis")

        result = self.analysis.main(f"{self.program_path}{self.program_name}.py")

        input_assmps = []
        for node, items in result.result.items():
            if node.identifier == 1:
                input_assmps = items[0].stack_top.assmps

        inputs = self.extract_inputs(input_assmps)

        print("Analysis done")

        print("Writing assumption to json")

        self.json_handler.input_assumptions_to_json(input_assmps, inputs)

    def extract_inputs(self, input_assmps) -> [str]:
        """Extracts input ids that are needed for relational constraints

        :param input_assmps: assumptions to extract the inputs ids from
        :return: list of extracted input ids
        """
        inputs = set()
        for assmp in input_assmps:
            if isinstance(assmp, MultiInputAssumptionLattice):
                inputs.add(assmp.iterations.var.name)
                inner_inputs = self.extract_inputs(assmp.assmps)
                inputs.update(inner_inputs)
            else:
                for relation in assmp.relations.relations:
                    inputs.add(relation.first.name)
                    inputs.add(relation.second.name)
        return inputs

    def run_checker(self) -> [ErrorInformation]:
        """Runs the input checker to compare inputs to assumptions gathered by the analysis.

        :return: List of errors found by the checker
        """
        print("Reading assumption from json")

        input_assumptions, inputs = self.json_handler.json_to_input_assumptions()

        print("Running input checker")

        errors = self.input_checker.check_input(input_assumptions, inputs)

        print("Input checking done")

        return errors

    def main(self) -> [ErrorInformation]:
        """Runs the analysis and input checker

        :return: List of errors found by the checker
        """
        self.run_analysis()
        return self.run_checker()

if __name__ == '__main__':
    QualityAnalysisRunner("example/", "checker_example", "checker_example.in").main()
