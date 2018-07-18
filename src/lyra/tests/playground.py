from lyra.engine.assumption.assumption_analysis import TypeAnalysis, RangeAnalysis, \
    TypeRangeAssumptionAnalysis
from lyra.engine.liveness.liveness_analysis import LivenessAnalysis, StrongLivenessAnalysis
from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysis
from lyra.engine.numerical.interval_analysis import BackwardIntervalAnalysis
from lyra.engine.usage.usage_analysis import SimpleUsageAnalysis

# LivenessAnalysis().main("liveness/example.py")

# StrongLivenessAnalysis().main("liveness/example.py")

# SimpleUsageAnalysis().main("usage/example.py")

# ForwardIntervalAnalysis().main("numerical/example.py")

# BackwardIntervalAnalysis().main("assumption/example.py")

# TypeAnalysis().main("assumption/example.py")
# RangeAnalysis().main("assumption/example.py")
TypeRangeAssumptionAnalysis().main("assumption/example.py")
