from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.input_checker.input_checker import InputChecker
from lyra.quality_analysis.json_handler import JSONHandler
from lyra.quality_analysis.static_analyzer.input_assumption_collector import \
    InputAssumptionCollector


def run_analysis(python_file_name):
    print("Running analysis")

    result = AssumptionAnalysis().main(f"../tests/quality/{python_file_name}.py", False)

    for block, analysis in result.result.items():
        if block.identifier == 1:
            assumption_lattice = analysis[0].store[analysis[0].input_var]
            break
    if assumption_lattice is None:
        raise Exception("Cannot find input assumption in analysis result.")
    assumptions = assumption_lattice.assumptions

    print("Collecting result")

    assumption_collector = InputAssumptionCollector(result.cfg, assumptions)
    input_assumptions = assumption_collector.collect_input_assumptions()

    print("Analysis done")

    print("Writing assumption to json")

    JSONHandler().input_assumptions_to_json(python_file_name, input_assumptions)


def run_checker(python_file_name):
    print("Reading assumption from json")

    input_assumptions = JSONHandler().json_to_input_assumptions(python_file_name)

    print("Running input checker")

    InputChecker(python_file_name).check_input(python_file_name, input_assumptions)

    print("Input checking done")


def main(python_file_name):
    run_analysis(python_file_name)
    run_checker(python_file_name)

if __name__ == '__main__':
    curr_python_file_name = "example"
    main(curr_python_file_name)
    #run_checker(curr_python_file_name)