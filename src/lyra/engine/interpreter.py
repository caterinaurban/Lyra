"""
Analysis Engine
===============

:Author: Caterina Urban
"""

from abc import ABCMeta, abstractmethod
from typing import Dict

from lyra.core.cfg import ControlFlowGraph
from lyra.engine.result import AnalysisResult

from lyra.abstract_domains.state import State


class Interpreter(metaclass=ABCMeta):
    def __init__(self, cfgs, fargs, semantics, widening, precursory=None):
        """Control flow graph interpreter.

        :param cfgs: control flow graphs to analyze
        :param fargs: formal arguments of functions
        :param semantics: semantics of statements in the control flow graph
        :param widening: number of iterations before widening
        :param precursory: precursory control flow graph interpreter
        """
        self._result = AnalysisResult(cfgs)
        self._fargs = fargs
        self._semantics = semantics
        self._widening: int = widening
        self._precursory: 'Interpreter' = precursory

    @property
    def cfgs(self):
        return self.result.cfgs

    @property
    def fargs(self):
        return self._fargs

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
    def analyze(self, cfg: ControlFlowGraph, initial: State) -> AnalysisResult:
        """Run the analysis.

        :param cfg: control flow graph to analyze
        :param initial: initial analysis state
        :return: result of the analysis
        """
