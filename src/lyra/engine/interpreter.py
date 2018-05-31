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
    def __init__(self, cfg: ControlFlowGraph, semantics, widening, initial):
        """Control flow graph interpreter.
        
        :param cfg: control flow graph to analyze
        :param semantics: semantics of statements in the control flow graph
        :param widening: number of iterations before widening
        :param initial: initial analysis state
        """
        self._result = AnalysisResult(cfg)
        self._semantics: Semantics = semantics
        self._widening: int = widening
        self._initial: State = initial

    @property
    def result(self):
        return self._result

    @property
    def cfg(self):
        return self.result.cfg

    @property
    def semantics(self):
        return self._semantics

    @property
    def widening(self):
        return self._widening

    @property
    def initial(self):
        return self._initial

    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """Run the analysis.

        :return: result of the analysis
        """
