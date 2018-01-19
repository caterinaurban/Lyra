from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.InputAssumptionSimplification import InputAssumptionSimplification
from lyra.quality_analysis.input_checker import InputChecker
from lyra.quality_analysis.json_handler import JSONHandler


class QualityAnalysisRunner:

    def __init__(self, program_path, program_name, input_file_name):
        self.program_path = program_path
        self.program_name = program_name
        self.analysis = AssumptionAnalysis(False)
        self.json_handler = JSONHandler(program_path, program_name)
        self.input_checker = InputChecker(program_path, input_file_name, program_name)
        self.assmp_simplification = InputAssumptionSimplification()

    def run_analysis(self):
        """Runs the quality analysis."""
        print("Running analysis")

        result = self.analysis.main(f"{self.program_path}{self.program_name}.py")

        input_assumptions = self.assmp_simplification.analysis_result_to_simple_assmps(result)

        print("Analysis done")

        print("Writing assumption to json")

        self.json_handler.input_assumptions_to_json(input_assumptions)

    def run_checker(self):
        """Runs the input checker to compare inputs to assumptions gathered by the analysis."""
        print("Reading assumption from json")

        input_assumptions = self.json_handler.json_to_input_assumptions()

        print("Running input checker")

        errors = self.input_checker.check_input(input_assumptions)

        print("Input checking done")

        return errors

    def main(self):
        self.run_analysis()
        return self.run_checker()

if __name__ == '__main__':
    QualityAnalysisRunner("example/", "checker_example", "checker_example.in").main()
