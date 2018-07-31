from lyra.engine.container.fulara.fulara_analysis import DictContentAnalysis

# LivenessAnalysis().main("liveness/example.py")
# StrongLivenessAnalysis().main("liveness/example.py")

# SimpleUsageAnalysis().main("usage/example.py")

# ForwardIntervalAnalysis().main("numerical/forward/example.py")
# BackwardIntervalAnalysis().main("numerical/backward/example.py")

# BackwardSignAnalysis().main("numerical/backward/example.py")

# TypeAnalysis().main("assumption/example.py")
# RangeAnalysis().main("assumption/example.py")
# TypeRangeAssumptionAnalysis().main("assumption/example.py")

DictContentAnalysis().main("numerical/larger_expressions.py")