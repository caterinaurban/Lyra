from lyra.engine.liveness.liveness_analysis import LivenessAnalysis
from lyra.engine.numerical.interval_analysis import IntervalAnalysis
from lyra.engine.usage.usage_analysis import UsageAnalysis

LivenessAnalysis().main("liveness/example.py")

# UsageAnalysis().main("usage/example.py")

# IntervalAnalysis().main("numerical/example.py")
