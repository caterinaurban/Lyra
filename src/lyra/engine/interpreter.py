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
    def __init__(self, cfg: ControlFlowGraph, semantics: Semantics, widening: int):
        """Control flow graph interpreter.
        
        :param cfg: control flow graph to analyze
        :param semantics: semantics of statements in the control flow graph
        :param widening: number of iterations before widening
        """
        self._result = AnalysisResult(cfg)
        self._semantics = semantics
        self._widening = widening

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

    @abstractmethod
    def analyze(self, initial: State) -> AnalysisResult:
        """Run the analysis.
        
        :param initial: initial analysis state
        :return: result of the analysis
        """
