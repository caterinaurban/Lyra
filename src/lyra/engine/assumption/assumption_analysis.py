"""
Assumption Analysis
===================

:Author: Caterina Urban and Madelin Schumacher
"""
from lyra.abstract_domains.assumption.alphabet_domain import AlphabetState
from lyra.abstract_domains.assumption.assumption_domain import TypeRangeAssumptionState, \
    TypeAlphabetAssumptionState, TypeRangeAlphabetAssumptionState, TypeQuantityAssumptionState, \
    TypeWordSetAssumptionState, TypeRangeWordSetAssumptionState, \
    TypeRangeAlphabetWordSetAssumptionState, QuantityRangeWordSetAssumptionState, \
    SignIntervalStringSetProductState, TypeSignIntervalStringSetProductState, \
    TypeQuantityRangeWordSetAssumptionState
from lyra.abstract_domains.assumption.quantity_domain import QuantityState
from lyra.abstract_domains.assumption.range_domain import RangeState
from lyra.abstract_domains.assumption.type_domain import TypeState
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.forward import ForwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.semantics.forward import DefaultForwardSemantics


class ForwardTypeAnalysis(Runner):

    def interpreter(self):
        return ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)

    def state(self):
        return TypeState(self.variables)


class BackwardTypeAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeState(self.variables)


class QuantityAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return QuantityState(self.variables)


class RangeAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return RangeState(self.variables)


class AlphabetAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return AlphabetState(self.variables)


class TypeQuantityAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeQuantityAssumptionState(self.variables)


class TypeRangeAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAssumptionState(self.variables)


class TypeAlphabetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeAlphabetAssumptionState(self.variables)


class TypeWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeWordSetAssumptionState(self.variables)


class TypeRangeAlphabetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAlphabetAssumptionState(self.variables)


class TypeRangeWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeWordSetAssumptionState(self.variables)


class TypeRangeAlphabetWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAlphabetWordSetAssumptionState(self.variables)


class QuantityRangeWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        forward = ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3, precursory=forward)

    def state(self):
        precursory = SignIntervalStringSetProductState(self.variables)
        return QuantityRangeWordSetAssumptionState(self.variables, precursory=precursory)

class TypeQuantityRangeWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        forward = ForwardInterpreter(self.cfgs, self.fargs, DefaultForwardSemantics(), 3)
        return BackwardInterpreter(self.cfgs, self.fargs, DefaultBackwardSemantics(), 3, precursory=forward)

    def state(self):
        precursory = TypeSignIntervalStringSetProductState(self.variables)
        return TypeQuantityRangeWordSetAssumptionState(self.variables, precursory=precursory)
