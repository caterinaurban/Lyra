import argparse

from lyra.engine.liveness.liveness_analysis import LivenessAnalysis
from lyra.engine.numerical.interval_analysis import IntervalAnalysis
from lyra.engine.usage.usage_analysis import UsageAnalysis


def main():
    """ Static analyzer entry point. """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'python_file',
        help='Python file to analyze')
    parser.add_argument(
        '--analysis',
        help='analysis to be used (usage or liveness)',
        default='usage')
    args = parser.parse_args()

    if args.analysis is 'intervals':
        IntervalAnalysis().main(args.python_file)
    if args.analysis is 'liveness':
        LivenessAnalysis().main(args.python_file)
    if args.analysis is 'usage':
        UsageAnalysis().main(args.python_file)


if __name__ == '__main__':
    main()
