#####################
# Liveness Analyses #
#####################

# from lyra.engine.liveness.liveness_analysis import LivenessAnalysis
# LivenessAnalysis().main("esop2018.py")

# from lyra.engine.liveness.liveness_analysis import StrongLivenessAnalysis
# StrongLivenessAnalysis().main("example.py")

# from lyra.engine.liveness.fulara_liveness_analysis import FularaIntervalLivenessAnalysis
# FularaIntervalLivenessAnalysis().main("usage/running_example.py")

##################
# Usage Analyses #
##################

# from lyra.engine.usage.usage_analysis import SimpleUsageAnalysis
# SimpleUsageAnalysis().main("example.py")

# from lyra.engine.usage.fulara_usage_analysis import FularaIntervalUsageAnalysis
# FularaIntervalUsageAnalysis().main("usage/running_example.py")

######################
# Numerical Analyses #
######################

# from lyra.engine.numerical.sign_analysis import ForwardSignAnalysis
# ForwardSignAnalysis().main("example.py")

# from lyra.engine.numerical.sign_analysis import BackwardSignAnalysis
# BackwardSignAnalysis().main("example.py")

# from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysisWithSummarization
# ForwardIntervalAnalysisWithSummarization().main("example.py")

# from lyra.engine.numerical.interval_analysis import ForwardIntervalAnalysisWithIndexing
# ForwardIntervalAnalysisWithIndexing().main("example.py")

# ForwardIntervalAnalysis().main("code_jam/alphabet_cake/cake_altafen.py")                # OK (super slow, 95s)
# ForwardIntervalAnalysis().main("code_jam/alphabet_cake/cake_bambit.py")                 # OK
# ForwardIntervalAnalysis().main("code_jam/alphabet_cake/cake_code14.py")                 # OK
# ForwardIntervalAnalysis().main("code_jam/alphabet_cake/cake_eduardische.py")            # OK
# ForwardIntervalAnalysis().main("code_jam/alphabet_cake/cake_jaymanmsu.py")              # OK
# ForwardIntervalAnalysis().main("code_jam/alphabet_cake/cake_karlSt.py")                 # NotImplementedError: Missing visitor for Items in IntervalState.ExpressionEvaluation!
# ForwardIntervalAnalysis().main("code_jam/alphabet_cake/cake_rojko.py")                  # RECURSION
#
# ForwardIntervalAnalysis().main("code_jam/beaming_with_joy/beaming_romd.py")             # ValueError: Call to split of unexpected argument temp[index]!
#
# ForwardIntervalAnalysis().main("code_jam/fashion_show/fashion_bemethor.py")             # OK
# ForwardIntervalAnalysis().main("code_jam/fashion_show/fashion_cypi.py")                 # OK
# ForwardIntervalAnalysis().main("code_jam/fashion_show/fashion_devjoe.py")               # KeyError: 'index'
# ForwardIntervalAnalysis().main("code_jam/fashion_show/fashion_gepa.py")                 # ValueError: Unexpected expression during sequence length computation.
# ForwardIntervalAnalysis().main("code_jam/fashion_show/fashion_haidamoo.py")             # OK (slow, 45s)
# ForwardIntervalAnalysis().main("code_jam/fashion_show/fashion_jksdf.py")                # OK
#
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_arctice.py")          # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_billjeff.py")         # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_bovard.py")           # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_fyodr.py")            # RECURSION
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_gahou.py")            # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_jsphkn.py")           # RECURSION
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_masterginger.py")     # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_mofhu.py")            # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_paragonLight.py")     # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_real.py")             # OK
# ForwardIntervalAnalysis().main("code_jam/pancake_flipper/pancakes_trevorSwope.py")      # OK

# from lyra.engine.numerical.interval_analysis import ForwardBoxAnalysis
# ForwardBoxAnalysis().main("example.py")

# from lyra.engine.numerical.interval_analysis import BackwardIntervalAnalysisWithSummarization
# BackwardIntervalAnalysisWithSummarization().main("example.py")

# from lyra.engine.numerical.octagon_analysis import ForwardOctagonAnalysis
# ForwardOctagonAnalysis().main("example.py")

# from lyra.engine.numerical.polyhedra_analysis import ForwardPolyhedraAnalysis
# ForwardPolyhedraAnalysis().main("example.py")

# from lyra.engine.numerical.polyhedra_analysis import BackwardPolyhedraAnalysis
# BackwardPolyhedraAnalysis().main("example.py")

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

# from lyra.engine.assumption.assumption_analysis import ForwardTypeAnalysis
# ForwardTypeAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import BackwardTypeAnalysis
# BackwardTypeAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import RangeAnalysis
# RangeAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import AlphabetAnalysis
# AlphabetAnalysis().main("example.py")

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

# from lyra.engine.assumption.assumption_analysis import QuantityRangeWordSetAssumptionAnalysis
# QuantityRangeWordSetAssumptionAnalysis().main("example.py")

# from lyra.engine.assumption.assumption_analysis import TypeSignIntervalStringSetProductAnalysis
# TypeSignIntervalStringSetProductAnalysis().main("example.py")

# TypeSignIntervalStringSetProductAnalysis().main("code_jam/alphabet_cake/cake_altafen.py")                # OK (suspiciously not slow) <===
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/alphabet_cake/cake_bambit.py")                 # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/alphabet_cake/cake_code14.py")                 # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/alphabet_cake/cake_eduardische.py")            # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/alphabet_cake/cake_jaymanmsu.py")              # AttributeError: 'TupleLyraType' object has no attribute 'typ' <===
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/alphabet_cake/cake_karlSt.py")                 # NotImplementedError: Missing visitor for Items in IntervalState.ExpressionEvaluation!
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/alphabet_cake/cake_rojko.py")                  # RECURSION
#
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/beaming_with_joy/beaming_romd.py")             # ValueError: Call to split of unexpected argument temp[index]!
#
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/fashion_show/fashion_bemethor.py")             # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/fashion_show/fashion_cypi.py")                 # AttributeError: 'TupleLyraType' object has no attribute 'typ' <===
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/fashion_show/fashion_devjoe.py")               # KeyError: 'index'
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/fashion_show/fashion_gepa.py")                 # ValueError: Unexpected expression during sequence length computation.
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/fashion_show/fashion_haidamoo.py")             # OK (suspiciously not slow) <===
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/fashion_show/fashion_jksdf.py")                # OK
#
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_arctice.py")          # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_billjeff.py")         # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_bovard.py")           # ValueError: Unexpected expression during sequence length computation. <===
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_fyodr.py")            # RECURSION
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_gahou.py")            # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_jsphkn.py")           # RECURSION
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_masterginger.py")     # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_mofhu.py")            # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_paragonLight.py")     # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_real.py")             # OK
# TypeSignIntervalStringSetProductAnalysis().main("code_jam/pancake_flipper/pancakes_trevorSwope.py")      # OK

# from lyra.engine.assumption.assumption_analysis import TypeQuantityRangeWordSetAssumptionAnalysis
# TypeQuantityRangeWordSetAssumptionAnalysis().main("example.py")
