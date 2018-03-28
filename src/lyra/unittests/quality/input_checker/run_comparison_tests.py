import glob
import os
import filecmp

from lyra.quality_analysis.run_analysis import QualityAnalysisRunner


class InputCheckerTests:

    def run_tests(self):
        program_path = os.getcwd() + '/'
        jsons = program_path + "**.json"
        num_tests_correct = 0
        for path in glob.iglob(jsons):
            program_name = path.split('/')[-1].split('.')[0]
            QualityAnalysisRunner(program_path, program_name, f"{program_name}.in").run_checker()
            file_err_name = f"errors_{program_name}.txt"
            file_err = program_path + file_err_name
            file_err_exp_name = f"errors_{program_name}_expected.txt"
            file_err_expected = program_path + file_err_exp_name
            same_err = filecmp.cmp(file_err, file_err_expected)
            if not same_err:
                print(f"Error files '{file_err_name}' and '{file_err_exp_name}' do not match.")
            else:
                num_tests_correct += 1
        print(f"Successful tests: {num_tests_correct}")


if __name__ == "__main__":
    InputCheckerTests().run_tests()
