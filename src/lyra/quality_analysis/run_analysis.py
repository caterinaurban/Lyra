from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.input_checker.input_checker import InputChecker
from lyra.quality_analysis.json_handler import JSONHandler


def main():
    print("Running analysis")

    result = AssumptionAnalysis().main("../tests/quality/interm_example.py", True)

    print("Analysis done")

    for block, analysis in result.result.items():
        if block.identifier == 1:
            assumption_lattice = analysis[0].store[analysis[0].input_var]
            break
    if assumption_lattice is None:
        raise Exception("Cannot find input assumption in analysis result.")
    input_assumptions = list(reversed(assumption_lattice.assumptions))

    print("Writing assumption to json")

    program_name = "interm_example"
    json_handler = JSONHandler()
    json_handler.input_assumptions_to_json(program_name, input_assumptions)

    # print("Reading assumption from json")

    # input_assumptions_from_json = json_handler.json_to_input_assumptions(program_name)

    print('Running input checker')

    InputChecker(program_name).check_input('interm_input.in', input_assumptions)

    print('Input checking done')

if __name__ == '__main__':
    main()