from lyra.quality_analysis.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.input_checker import InputChecker
from lyra.quality_analysis.json_handler import JSONHandler


class QualityAnalysisRunner:

    def run_analysis(self, program_path, program_name):
        print("Running analysis")

        result = AssumptionAnalysis().main(f"{program_path}{program_name}.py")

        assumption_lattice = None
        for block, analysis in result.result.items():
            if block.identifier == 1:
                assumption_lattice = analysis[0].store[analysis[0].input_var]
                break
        if assumption_lattice is None:
            raise Exception("Cannot find input assumption in analysis result.")
        input_assumptions = assumption_lattice.lattice.assmps

        print("Analysis done")

        print("Writing assumption to json")

        json_handler = JSONHandler(program_path, program_name)
        json_handler.input_assumptions_to_json(input_assumptions)

    def run_checker(self, program_path, program_name, input_file_name):
        print("Reading assumption from json")

        json_handler = JSONHandler(program_path, program_name)
        input_assumptions = json_handler.json_to_input_assumptions()

        print("Running input checker")

        checker = InputChecker(program_path, input_file_name, program_name)
        errors = checker.check_input(input_assumptions)

        print("Input checking done")

        return errors

    def main(self, program_path, program_name, input_file_name):
        self.run_analysis(program_path, program_name)
        return self.run_checker(program_path, program_name, input_file_name)

if __name__ == '__main__':
    QualityAnalysisRunner().main("example/", "checker_example", "checker_example.in")
