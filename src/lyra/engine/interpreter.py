"""
Analysis Engine
===============

:Author: Caterina Urban
"""

from abc import ABCMeta, abstractmethod

from lyra.core.cfg import ControlFlowGraph
from lyra.engine.result import AnalysisResult

from lyra.abstract_domains.state import State
from lyra.semantics.semantics import Semantics


class Interpreter(metaclass=ABCMeta):
    def __init__(self, cfg: ControlFlowGraph, semantics, widening, precursory=None):
        """Control flow graph interpreter.

        :param cfg: control flow graph to analyze
        :param semantics: semantics of statements in the control flow graph
        :param widening: number of iterations before widening
        :param precursory: precursory control flow graph interpreter
        """
        self._result = AnalysisResult(cfg)
        self._semantics: Semantics = semantics
        self._widening: int = widening
        self._precursory: 'Interpreter' = precursory

    @property
    def cfg(self):
        return self.result.cfg

    @property
    def result(self):
        return self._result

    @property
    def semantics(self):
        return self._semantics

    @property
    def widening(self):
        return self._widening

    @property
    def precursory(self):
        return self._precursory

    @abstractmethod
    def analyze(self, initial: State) -> AnalysisResult:
        """Run the analysis.

        :param initial: initial analysis state
        :return: result of the analysis
        """
