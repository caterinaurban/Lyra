"""
Assumption Analysis
===================

:Author: Caterina Urban and Madelin Schumacher
"""
from typing import List

from lyra.abstract_domains.assumption.assumption_domain import TypeRangeAssumptionState, AssumptionState, \
    OctagonStringAssumptionState
from lyra.abstract_domains.assumption.character_domain import CharacterState
from lyra.abstract_domains.assumption.range_domain import RangeState
from lyra.abstract_domains.assumption.type_domain import TypeState
from lyra.abstract_domains.state import State
from lyra.core.expressions import Identifier, LengthIdentifier
from lyra.core.types import ListLyraType, StringLyraType
from lyra.engine.backward import BackwardInterpreter
from lyra.engine.runner import Runner
from lyra.semantics.backward import DefaultBackwardSemantics


class TypeAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeState(self.variables)


class RangeAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return RangeState(self.variables)


class TypeRangeAssumptionAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return TypeRangeAssumptionState(self.variables)


class CharacterDomainAnalysis(Runner):

    def interpreter(self):
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return CharacterState(self.variables)


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
        return BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)

    def state(self):
        return OctagonStringAssumptionState(self.variables)

    def run(self):
        result = self.interpreter().analyze(self.state())
        if self.show_simple:
            for node, items in result.result.items():
                if node.identifier == 1:
                    items[0] = items[0].stack_top.assmps
        if self.do_render:
            self.render(result)
        return result
