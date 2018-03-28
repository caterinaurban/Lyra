from shutil import copyfile

import os
import subprocess

from lyra.quality_analysis.input_checker import InputChecker, ErrorInformation
from lyra.quality_analysis.input_correction_view import InputCorrection
from lyra.quality_analysis.json_handler import JSONHandler
from lyra.quality_analysis.run_analysis import QualityAnalysisRunner


class DataQualityController:
    """Controller for the input correction application."""
    def __init__(self):
        self.input_checker = None
        self.input_correction = None
        self.program_name = None
        self.input_filename = None
        self.path = "example/"
        self.json_info = None

    def run(self):
        """Starts the input correction application."""
        self.input_correction = InputCorrection(self)
        self.input_correction.mainloop()

    def check_new_val(self, error: ErrorInformation) -> ErrorInformation:
        """Checks if a value fulfils an assumption

        :param error: the current error that should be checked
        :return: the error with an adapted error message or None if no error was found
        """
        return self.input_checker.check_new_value(error)

    def start_checking(self, program_name: str, input_filename: str) -> [ErrorInformation]:
        """Starts the input checking. If a JSON file already exists it will be used to do the
        checking, otherwise the analysis will run first.

        :param program_name: name of the python program that will be analyzed
        :param input_filename: name of the input file
        :return: errors found by the input checker
        """
        self.program_name = program_name
        self.input_filename = input_filename
        self.input_checker = InputChecker(self.path, self.input_filename, self.program_name)
        if not os.path.isfile(f"{self.path}{program_name}.json"):
            analysis = QualityAnalysisRunner(self.path, self.program_name, self.input_filename)
            analysis.run_analysis()
        json_handler = JSONHandler(self.path, self.program_name)
        self.json_info = json_handler.json_to_input_assumptions()
        errors = self.run_checker()
        if len(errors) == 0:
            return self.execute_input_program()
        return self.run_checker()

    def run_checker(self):
        """Runs the input checker."""
        input_assumptions, inputs = self.json_info
        return self.input_checker.check_input(input_assumptions, inputs)

    def check_corrected_input(self, error: ErrorInformation) -> [ErrorInformation]:
        """Writes the new values back to the input file and runs the input checker.

        :param error: error with information about new values
        :return: errors found by the input checker
        """
        new_values = [(error.infos1.location, error.infos1.orig_value)]
        if error.infos2 is not None:
            new_values.append((error.infos2.location, error.infos2.orig_value))
        new_values = sorted(new_values, key=lambda val: val[0])
        self.write_new_values(new_values)
        errors = self.run_checker()
        if len(errors) == 0:
            return self.execute_input_program()
        return errors

    def write_new_values(self, new_values):
        """Writes the new values to the input file.

        :param new_values: sorted List of tuples (location, new value)
        """
        curr_val_index = 0
        curr_loc = new_values[curr_val_index][0].file_line
        with open(self.path + self.input_filename, "r") as input_file:
            with open(self.path + self.input_filename + ".temp", "w") as input_file_tmp:
                line_num = 0
                line = ""
                last_line_newline = True
                while curr_val_index < len(new_values) or line:
                    line = input_file.readline()
                    if line_num == curr_loc:
                        if not last_line_newline:
                            input_file_tmp.write("\n")
                            last_line_newline = True
                        input_file_tmp.write(new_values[curr_val_index][1])
                        input_file_tmp.write("\n")
                        curr_val_index += 1
                        if curr_val_index < len(new_values):
                            curr_loc = new_values[curr_val_index][0].file_line
                        else:
                            curr_loc = -1
                    else:
                        input_file_tmp.write(line)
                        last_line_newline = line.endswith("\n")

                    line_num += 1
        copyfile(self.path + self.input_filename + ".temp", self.path + self.input_filename)
        os.remove(self.path + self.input_filename + ".temp")

    def execute_input_program(self):
        """Executes the analyzed program using the input data."""
        run_command = ["python", f"{self.path}{self.program_name}.py"]
        input_file = open(self.path + self.input_filename, "r")
        input_data = "".join(input_file.readlines())
        input_file.close()
        p = subprocess.run(run_command, stdout=subprocess.PIPE, input=input_data, encoding="utf-8")
        return [p.stdout]

if __name__ == "__main__":
    DataQualityController().run()
