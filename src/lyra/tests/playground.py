#####################
# Liveness Analyses #
#####################

# from lyra.engine.liveness.liveness_analysis import LivenessAnalysis
# LivenessAnalysis().main("esop2018.py")

# from lyra.engine.liveness.liveness_analysis import StrongLivenessAnalysis
# StrongLivenessAnalysis().main("esop2018.py")

# from lyra.engine.liveness.fulara_liveness_analysis import FularaIntervalLivenessAnalysis
# FularaIntervalLivenessAnalysis().main("usage/running_example.py")

##################
# Usage Analyses #
##################

# from lyra.engine.usage.usage_analysis import SimpleUsageAnalysis
# SimpleUsageAnalysis().main("esop2018.py")

# from lyra.engine.usage.fulara_usage_analysis import FularaIntervalUsageAnalysis
# FularaIntervalUsageAnalysis().main("usage/running_example.py")

######################
# Numerical Analyses #
######################

# from lyra.engine.numerical.sign_analysis import ForwardSignAnalysis
# ForwardSignAnalysis().main("example.py")

# from lyra.engine.numerical.sign_analysis import BackwardSignAnalysis
# BackwardSignAnalysis().main("example.py")

#from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysis
#ForwardIntervalAnalysis().main("example.py")

# from lyra.engine.numerical.interval_analysis import ForwardBoxAnalysis
# ForwardBoxAnalysis().main("example.py")

# from lyra.engine.numerical.interval_analysis import BackwardIntervalAnalysis
# BackwardIntervalAnalysis().main("example.py")

# from lyra.engine.numerical.polyhedra_analysis import ForwardPolyhedraAnalysis
# ForwardPolyhedraAnalysis().main("example.py")

# from lyra.engine.numerical.polyhedra_analysis import BackwardPolyhedraAnalysis
# BackwardPolyhedraAnalysis().main("example.py")

# from lyra.engine.container.fulara.fulara_analysis import FularaIntervalAnalysis
# FularaIntervalAnalysis().main("larger_expressions.py")

###################
# String Analyses #
###################

# from lyra.engine.string.character_analysis import ForwardCharacterAnalysis
# ForwardCharacterAnalysis().main("example.py")

# from lyra.engine.string.character_analysis import BackwardCharacterAnalysis
# BackwardCharacterAnalysis().main("example.py")

# from lyra.engine.string.stringset_analysis import ForwardStringSetAnalysis
# ForwardStringSetAnalysis().main("example.py")

# from lyra.engine.string.stringset_analysis import BackwardStringSetAnalysiss
# BackwardStringSetAnalysiss().main("example.py")

##################################
# Input Data Assumption Analyses #
##################################

# from lyra.engine.assumption.assumption_analysis import TypeAnalysis
# TypeAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import RangeAnalysis
# RangeAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import AlphabetAnalysis
# AlphabetAnalysis().main("example.py")

from lyra.engine.assumption.assumption_analysis import ContainerAnalysis
ContainerAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import TypeQuantityAssumptionAnalysis
# TypeQuantityAssumptionAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import TypeRangeAssumptionAnalysis
# TypeRangeAssumptionAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import TypeAlphabetAssumptionAnalysis
# TypeAlphabetAssumptionAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import TypeWordSetAssumptionAnalysis
# TypeWordSetAssumptionAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import TypeRangeAlphabetAssumptionAnalysis
# TypeRangeAlphabetAssumptionAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import TypeRangeWordSetAssumptionAnalysis
# TypeRangeWordSetAssumptionAnalysis().main("example.py")
