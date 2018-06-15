from lyra.engine.assumption.assumption_analysis import TypeAnalysis
from lyra.engine.liveness.liveness_analysis import LivenessAnalysis, StrongLivenessAnalysis
from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysis
from lyra.engine.numerical.interval_analysis import BackwardIntervalAnalysis
from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.engine.usage.usage_analysis import SimpleUsageAnalysis

# LivenessAnalysis().main("liveness/example.py")

# StrongLivenessAnalysis().main("liveness/example.py")

# SimpleUsageAnalysis().main("usage/example.py")

# BoolTracesAnalysis().main("traces/example.py")

# BackwardIntervalAnalysis().main("quality/example.py")

# ForwardIntervalAnalysis().main("numerical/example.py")

# AssumptionAnalysis().main("quality/example.py")

TypeAnalysis().main("assumption/example.py")
