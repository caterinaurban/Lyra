from lyra.engine.liveness.liveness_analysis import LivenessAnalysis, StrongLivenessAnalysis
from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysis
from lyra.engine.numerical.interval_analysis import BackwardIntervalAnalysis
from lyra.engine.quality.assumption_analysis import AssumptionAnalysis
from lyra.engine.usage.usage_analysis import UsageAnalysis

# LivenessAnalysis().main("liveness/example.py")

# StrongLivenessAnalysis().main("liveness/example.py")

# UsageAnalysis().main("quality/interm_example.py")

# BoolTracesAnalysis().main("traces/example.py")

# BackwardIntervalAnalysis().main("quality/example.py")

# ForwardIntervalAnalysis().main("quality/example.py")

AssumptionAnalysis(show_simple=True).main("quality/example.py")
