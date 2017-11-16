from lyra.engine.liveness.liveness_analysis import LivenessAnalysis
from lyra.engine.numerical.interval_analysis import IntervalAnalysis
from lyra.engine.traces.traces_analysis import BoolTracesAnalysis
from lyra.engine.usage.usage_analysis import UsageAnalysis
from lyra.engine.numerical.backward_interval_analysis import BackwardIntervalAnalysis

LivenessAnalysis().main("liveness/example.py")

BoolTracesAnalysis().main("traces/example.py")

UsageAnalysis().main("usage/example.py")

IntervalAnalysis().main("numerical/example.py")

BackwardIntervalAnalysis().main("numerical/example_backwards.py")