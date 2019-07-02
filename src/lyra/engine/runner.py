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
from typing import Set

from lyra.core.cfg import Loop
from lyra.core.expressions import VariableIdentifier, LengthIdentifier
from lyra.core.statements import Assignment, VariableAccess, Call, TupleDisplayAccess
from lyra.core.types import SequenceLyraType
from lyra.engine.result import AnalysisResult
from lyra.frontend.cfg_generator import ast_to_cfgs
from lyra.frontend.cfg_generator import ast_to_function_args
from lyra.visualization.graph_renderer import AnalysisResultRenderer


class Runner:
    """Analysis runner."""

    def __init__(self):
        self._path = None
        self._source = None
        self._tree = None
        self._cfg = None
        self._cfgs = None
        self._function_args = {}
        self._partial_result = dict()

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
    def cfg(self):
        return self._cfg

    @cfg.setter
    def cfg(self, cfg):
        self._cfg = cfg

    @property
    def partial_result(self):
        return self._partial_result

    @partial_result.setter
    def partial_result(self, partial_result):
        self._partial_result = partial_result

    @abstractmethod
    def interpreter(self):
        """Control flow graph interpreter."""

    @abstractmethod
    def state(self):
        """Initial analysis state."""

    @property
    def variables(self) -> Set[VariableIdentifier]:
        variables = set()
        visited, worklist = set(), Queue()
        worklist.put(self.cfg.in_node)
        while not worklist.empty():
            current = worklist.get()
            if current.identifier not in visited:
                visited.add(current.identifier)
                for stmt in current.stmts:
                    if isinstance(stmt, Assignment) and isinstance(stmt.left, VariableAccess):
                        variable = stmt.left.variable
                        variables.add(variable)
                        if isinstance(variable.typ, SequenceLyraType):
                            variables.add(LengthIdentifier(variable))
                if isinstance(current, Loop):
                    edges = self.cfg.edges.items()
                    conds = [edge.condition for nodes, edge in edges if nodes[0] == current]
                    for cond in [c for c in conds if isinstance(c, Call)]:
                        for arg in cond.arguments:
                            if isinstance(arg, VariableAccess):
                                variable = arg.variable
                                variables.add(arg.variable)
                                if isinstance(variable.typ, SequenceLyraType):
                                    variables.add(LengthIdentifier(variable))
                            elif isinstance(arg, TupleDisplayAccess):
                                for i in arg.items:
                                    variables.add(i.variable)
                for node in self.cfg.successors(current):
                    worklist.put(node)
        return variables

    def main(self, path):
        self.path = path
        with open(self.path, 'r') as source:
            self.source = source.read()
            self.tree = ast.parse(self.source)
            self.names_to_cfgs = ast_to_cfgs(self.tree)
            self.cfg = self.names_to_cfgs['main']
            self.function_args = ast_to_function_args(self.tree)
        return self.run()

    def run(self) -> AnalysisResult:
        start = time.time()
        result = self.interpreter().analyze(self.state())
        result.result.update(self.partial_result)
        end = time.time()
        print('Time: {}s'.format(end - start))
        self.render(result)
        return result

    def render(self, result):
        renderer = AnalysisResultRenderer()
        data = (self.names_to_cfgs, result)
        name = os.path.splitext(os.path.basename(self.path))[0]
        label = f"CFG with Analysis Result for {name}"
        directory = os.path.dirname(self.path)
        renderer.render(data, filename=name, label=label, directory=directory, view=True)
