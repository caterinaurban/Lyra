from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.input_checker import InputChecker
from lyra.quality_analysis.input_correction_view import InputCorrection
from lyra.quality_analysis.json_handler import JSONHandler
from lyra.quality_analysis.run_analysis import QualityAnalysisRunner


class DataQualityController:
    """Controller for the input correction application."""
    def __init__(self):
        self.quality_analysis = QualityAnalysisRunner()
        self.input_correction = None
        self.json_handler = None
        self.input_checker = None
        self.program_name = None
        self.input_filename = None
        self.path = "example/"

    def run(self):
        """Starts the input correction application."""
        self.input_correction = InputCorrection(self)
        self.input_correction.mainloop()

    def run_analysis(self):
        """Runs the assumption analysis."""
        print("Running analysis")

        result = AssumptionAnalysis().main(f"{self.path}{self.program_name}.py", False)
        input_assumptions = self.extract_assumptions(result)

        print("Analysis done")

        print("Writing assumption to json")

        self.json_handler.input_assumptions_to_json(input_assumptions)

    def run_checker(self):
        """Runs the input checker.

        :return: the errors find by the input checker
        """
        print("Reading assumption from json")

        input_assumptions = self.json_handler.json_to_input_assumptions()

        print("Running input checker")

        errors = self.input_checker.check_input(input_assumptions)

        print("Input checking done")

        return errors

    def check_new_val(self, new_val, assmp):
        """Checks if the value fulfils the assumption

        :param new_val: value that should fulfil the assumption
        :param assmp: assumption that should be fulfilled
        :return: if the value fulfils the assumption
        """
        return self.input_checker.check_assmp(new_val, assmp)

    def start_analysis(self, program_name, input_filename):
        """Starts the assumtion analysis.

        :param program_name: name of the python program that will be analyzed
        :param input_filename: name of the input file
        :return: errors found by the input checker
        """
        self.program_name = program_name
        self.input_filename = input_filename
        self.json_handler = JSONHandler(self.path, self.program_name)
        self.input_checker = InputChecker(self.path, self.input_filename, self.program_name)
        self.run_analysis()
        return self.run_checker()

    def extract_assumptions(self, analysis_result):
        """ Extracts the input assumptions from an analysis result

        :param analysis_result: result of the analysis
        :return: assumptions about the input
        """
        assumption_lattice = None
        for block, analysis in analysis_result.result.items():
            if block.identifier == 1:
                assumption_lattice = analysis[0].store[analysis[0].input_var]
                break
        if assumption_lattice is None:
            raise Exception("Cannot find input assumption in analysis result.")
        return assumption_lattice.lattice.assmps

if __name__ == "__main__":
    DataQualityController().run()
