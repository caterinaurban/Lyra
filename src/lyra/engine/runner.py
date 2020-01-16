"""
Program Analysis
================

:Author: Caterina Urban
"""

import ast
import os
import time
from abc import abstractmethod
from queue import Queue
from typing import Dict, List, Set

from lyra.core.cfg import Loop, ControlFlowGraph
from lyra.core.expressions import VariableIdentifier, LengthIdentifier
from lyra.core.statements import Assignment, VariableAccess, Call, TupleDisplayAccess
from lyra.core.types import SequenceLyraType, ContainerLyraType
from lyra.engine.result import AnalysisResult
from lyra.frontend.cfg_generator import ast_to_cfgs
from lyra.frontend.cfg_generator import ast_to_fargs
from lyra.visualization.graph_renderer import AnalysisResultRenderer


class Runner:
    """Analysis runner."""

    def __init__(self):
        self._path = None
        self._source = None
        self._tree = None
        self._cfgs = None
        self._fargs = {}

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, tree):
        self._tree = tree

    @property
    def cfgs(self):
        return self._cfgs

    @cfgs.setter
    def cfgs(self, cfgs):
        self._cfgs = cfgs

    @property
    def fargs(self):
        return self._fargs

    @fargs.setter
    def fargs(self, fargs):
        self._fargs = fargs

    @abstractmethod
    def interpreter(self):
        """Control flow graph interpreter."""

    @abstractmethod
    def state(self):
        """Initial analysis state."""

    @property
    def variables(self, fname: str = '') -> Set[VariableIdentifier]:
        return self.cfgs[fname].variables

    def main(self, path):
        self.path = path
        with open(self.path, 'r') as source:
            self.source = source.read()
            self.tree = ast.parse(self.source)
            self.cfgs: Dict[str, ControlFlowGraph] = ast_to_cfgs(self.tree)
            self.fargs: Dict[str, List[VariableIdentifier]] = ast_to_fargs(self.tree)
        return self.run()

    def run(self, fname: str = '') -> AnalysisResult:
        start = time.time()
        result = self.interpreter().analyze(self.cfgs[fname], self.state())
        end = time.time()
        print('Time: {}s'.format(end - start))
        self.render(result)
        return result

    def render(self, result):
        renderer = AnalysisResultRenderer()
        data = (self.cfgs, result)
        name = os.path.splitext(os.path.basename(self.path))[0]
        label = f"CFG with Analysis Result for {name}"
        directory = os.path.dirname(self.path)
        renderer.render(data, filename=name, label=label, directory=directory, view=True)
