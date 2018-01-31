import glob
import os

from lyra.quality_analysis.run_analysis import QualityAnalysisRunner


class NoErrorTests:

    def run_tests(self):
        program_path = os.getcwd() + '/../analysis/relationships/'
        tests = program_path + '**.py'
        for path in glob.iglob(tests):
            if os.path.basename(path) == "__init__.py":
                continue
            program_name = path.split('/')[-1].split('.')[0]
            QualityAnalysisRunner(program_path, program_name, "generic.in").main()

            jsonfile = f"{program_path}{program_name}.json"
            if not os.path.isfile(jsonfile):
                print(f"No json file created for {program_name}")
            else:
                os.remove(jsonfile)

            errorfile = f"{program_path}errors_{program_name}.txt"
            if not os.path.isfile(errorfile):
                print(f"No error file created for {program_name}")
            else:
                os.remove(errorfile)


if __name__ == "__main__":
    NoErrorTests().run_tests()
