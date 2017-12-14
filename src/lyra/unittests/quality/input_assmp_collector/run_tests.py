from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.quality_analysis.static_analyzer.input_assumption_collector import \
    InputAssumptionCollector


def run_analysis(python_file_name):
    """
    Runs the analysis and checks if the assumptions collected by the InputAssumptionCollector
    match the ones given as a solution in this file
    """

    result = AssumptionAnalysis().main(f"{python_file_name}.py", False)

    for block, analysis in result.result.items():
        if block.identifier == 1:
            assumption_lattice = analysis[0].store[analysis[0].input_var]
            break
    if assumption_lattice is None:
        raise Exception("Cannot find input assumption in analysis result.")
    input_assmps = assumption_lattice.assumptions

    cfg = result.cfg
    return InputAssumptionCollector(cfg, input_assmps).collect_input_assumptions()

if __name__ == '__main__':
    tests = {"loop": "[(Int, [-inf, inf]), (Float, [-inf, inf]), (Float, [-inf, inf]), (Float, [-inf, inf]), (Int, [-inf, inf])]",
             "simple": "[(Int, [-inf, inf]), (Float, [-inf, inf]), (Any, [-inf, inf])]",
             "ifelse": "[(Int, [-inf, inf]), (Float, [-inf, inf]), (Any, [-inf, inf])]"
            }
    for test in tests.keys():
        final = run_analysis(test)
        print(test)
        print(tests[test])
        print(final)
        print()