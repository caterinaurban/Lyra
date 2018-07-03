"""
Program Analysis
================

:Author: Caterina Urban
"""

import ast
import os
from abc import abstractmethod
from queue import Queue
from typing import List

from lyra.core.cfg import Loop
from lyra.core.expressions import VariableIdentifier
from lyra.core.statements import Assignment, VariableAccess, Call
from lyra.engine.result import AnalysisResult

from lyra.frontend.cfg_generator import ast_to_cfg
from lyra.visualization.graph_renderer import AnalysisResultRenderer


class Runner:
    """Analysis runner."""

    def __init__(self):
        self._path = None
        self._source = None
        self._tree = None
        self._cfg = None

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

    @abstractmethod
    def interpreter(self):
        """Control flow graph interpreter."""

    @abstractmethod
    def state(self):
        """Initial analysis state."""

    @property
    def variables(self) -> List[VariableIdentifier]:
        variables = set()
        visited, worklist = set(), Queue()
        worklist.put(self.cfg.in_node)
        while not worklist.empty():
            current = worklist.get()
            if current.identifier not in visited:
                visited.add(current.identifier)
                for stmt in current.stmts:
                    if isinstance(stmt, Assignment) and isinstance(stmt.left, VariableAccess):
                        variables.add(stmt.left.variable)
                if isinstance(current, Loop):
                    edges = self.cfg.edges.items()
                    conds = [edge.condition for nodes, edge in edges if nodes[0] == current]
                    for cond in [c for c in conds if isinstance(c, Call)]:
                        for arg in [a for a in cond.arguments if isinstance(a, VariableAccess)]:
                            variables.add(arg.variable)
                for node in self.cfg.successors(current):
                    worklist.put(node)
        return sorted(variables, key=lambda x: x.name)

    def main(self, path):
        self.path = path
        with open(self.path, 'r') as source:
            self.source = source.read()
            self.tree = ast.parse(self.source)
            self.cfg = ast_to_cfg(self.tree)
        return self.run()

    def run(self) -> AnalysisResult:
        result = self.interpreter().analyze(self.state())
        self.render(result)
        return result

    def render(self, result):
        renderer = AnalysisResultRenderer()
        data = (self.cfg, result)
        name = os.path.splitext(os.path.basename(self.path))[0]
        label = f"CFG with Analysis Result for {name}"
        directory = os.path.dirname(self.path)
        renderer.render(data, filename=name, label=label, directory=directory, view=True)
