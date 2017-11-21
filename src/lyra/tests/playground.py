from lyra.engine.liveness.liveness_analysis import LivenessAnalysis, StrongLivenessAnalysis
from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysis
from lyra.engine.usage.usage_analysis import UsageAnalysis
from lyra.engine.numerical.backward_interval_analysis import BackwardIntervalAnalysis

# LivenessAnalysis().main("liveness/example.py")

# StrongLivenessAnalysis().main("liveness/example.py")

# UsageAnalysis().main("usage/example.py")

ForwardIntervalAnalysis().main("numerical/example.py")

#BackwardIntervalAnalysis().main("numerical/example_backwards.py")