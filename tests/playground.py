from engine.liveness.liveness_analysis import LivenessAnalysis
from engine.numerical.interval_analysis import IntervalAnalysis
from engine.numerical.backward_interval_analysis import BackwardIntervalAnalysis
from engine.traces.traces_analysis import BoolTracesAnalysis
from engine.usage.usage_analysis import UsageAnalysis
from abstract_domains.numerical.interval_domain import IntervalLattice

#LivenessAnalysis().main("liveness/example.py")

#BoolTracesAnalysis().main("traces/example.py")

#UsageAnalysis().main("usage/example.py")

IntervalAnalysis().main("numerical/example.py")

#BackwardIntervalAnalysis().main("numerical/example.py")
