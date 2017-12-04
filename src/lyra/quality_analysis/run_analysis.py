from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.input_checker.input_checker import InputChecker


def main():
    print('Running analysis')
    result = AssumptionAnalysis().main("../tests/quality/interm_example.py", False)
    print('Analysis done')
    for block, analysis in result.result.items():
        if block.identifier == 1:
            assumption_lattice = analysis[0].store[analysis[0].input_var]
            break
    if assumption_lattice is None:
        raise Exception('Cannot find input assumption in analysis result.')
    input_assumptions = list(reversed(assumption_lattice.assumptions))
    print('Running input checker')
    InputChecker().check_input('interm_input.in', input_assumptions, 'interm_example')
    print('Input checking done')

if __name__ == '__main__':
    main()