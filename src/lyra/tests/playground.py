from lyra.engine.assumption.assumption_analysis import TypeAnalysis, RangeAnalysis, \
    TypeRangeAssumptionAnalysis
from lyra.engine.liveness.liveness_analysis import LivenessAnalysis, StrongLivenessAnalysis
from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysis
from lyra.engine.numerical.interval_analysis import BackwardIntervalAnalysis
from lyra.engine.numerical.sign_analysis import BackwardSignAnalysis
from lyra.engine.usage.usage_analysis import SimpleUsageAnalysis

# LivenessAnalysis().main("liveness/example.py")
# StrongLivenessAnalysis().main("liveness/example.py")
#
# SimpleUsageAnalysis().main("usage/example.py")
#
# ForwardIntervalAnalysis().main("numerical/forward/example.py")
# BackwardIntervalAnalysis().main("numerical/backward/example.py")
#
# BackwardSignAnalysis().main("numerical/backward/example.py")
#
# # BackwardIntervalAnalysis().main("assumption/example.py")
TypeAnalysis().main("/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/madelin1.py")
# RangeAnalysis().main("assumption/example.py")
# TypeRangeAssumptionAnalysis().main("assumption/example.py")

CharacterDomainAnalysis().main('../unittests/character/filter.py')