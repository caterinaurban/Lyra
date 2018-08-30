"""
Assumption Analysis
===================

:Author: Caterina Urban and Madelin Schumacher
"""
from typing import List

from lyra.abstract_domains.assumption.alphabet_domain import AlphabetState
from lyra.abstract_domains.assumption.assumption_domain import TypeAlphabetAssumptionState, \
    TypeRangeAlphabetAssumptionState, TypeQuantityAssumptionState
from lyra.abstract_domains.assumption.assumption_domain import TypeRangeAssumptionState, \
    SignOctagonStringAssumptionState, TypeAlphabetAssumptionState, TypeRangeAlphabetAssumptionState, TypeQuantityAssumptionState, \
    TypeWordSetAssumptionState, TypeRangeWordSetAssumptionState, \
    TypeRangeAlphabetWordSetAssumptionState
from lyra.abstract_domains.assumption.quantity_domain import QuantityState
from lyra.abstract_domains.assumption.range_domain import RangeState
from lyra.abstract_domains.assumption.type_domain import TypeState
from lyra.core.expressions import Identifier, LengthIdentifier
from lyra.core.types import ListLyraType, StringLyraType
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.assumption import AssumptionDefaultBackwardSemantics
from lyra.semantics.backward import DefaultBackwardSemantics


class TypeAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeState(self.variables)


class QuantityAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return QuantityState(self.variables)


class RangeAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return RangeState(self.variables)


class AlphabetAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return AlphabetState(self.variables)


class TypeQuantityAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, AssumptionDefaultBackwardSemantics(), 3)

    def state(self):
        return TypeQuantityAssumptionState(self.variables)


class TypeRangeAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAssumptionState(self.variables)


class TypeAlphabetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeAlphabetAssumptionState(self.variables)


class TypeWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeWordSetAssumptionState(self.variables)


class TypeRangeAlphabetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAlphabetAssumptionState(self.variables)


class AlphabetDomainAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return AlphabetState(self.variables)


class AssumptionAnalysis(Runner):

    def __init__(self, do_render=False, show_simple=False):
        super().__init__()
        self.do_render = do_render
        self.show_simple = show_simple

    @property
    def variables(self) -> List[Identifier]:
        variables_list = super().variables
        variables = set(variables_list)
        for var in variables_list:
            if isinstance(var.typ, ListLyraType) or isinstance(var.typ, StringLyraType):
                length_var = LengthIdentifier(var)
                if length_var in variables:
                    continue
                variables.add(length_var)
        return sorted(variables, key=lambda x: x.name)

    def interpreter(self):
        return BackwardInterpreter(self.cfg, AssumptionDefaultBackwardSemantics(), 3)

    def state(self):
        return SignOctagonStringAssumptionState(self.variables)

    def run(self):
        result = self.interpreter().analyze(self.state())
        if self.show_simple:
            for node, items in result.result.items():
                if node.identifier == 1:
                    items[0] = items[0].stack_top.assmps
        if self.do_render:
            self.render(result)
        return result


class TypeRangeWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeWordSetAssumptionState(self.variables)


class TypeRangeAlphabetWordSetAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAlphabetWordSetAssumptionState(self.variables)
