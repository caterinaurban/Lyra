"""
Program Analysis
================

:Author: Caterina Urban
"""

import ast
import io
import os
import re
import time
import tokenize
from abc import abstractmethod
from math import inf
from queue import Queue
from typing import Dict, List, Set

from lyra.core.cfg import Loop, ControlFlowGraph, Conditional, Edge, Node
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
        self.check(result)
        return result

    def render(self, result):
        renderer = AnalysisResultRenderer()
        data = (self.cfgs, result)
        name = os.path.splitext(os.path.basename(self.path))[0]
        label = f"CFG with Analysis Result for {name}"
        directory = os.path.dirname(self.path)
        renderer.render(data, filename=name, label=label, directory=directory, view=True)

    def _expected_result(self):
        initial = re.compile('INITIAL:?\s*(?P<state>.*)')
        state = re.compile('STATE:?\s*(?P<state>.*)')
        loop = re.compile('LOOP:?\s*(?P<state>.*)')
        final = re.compile('FINAL:?\s*(?P<state>.*)')
        for token in tokenize.tokenize(io.BytesIO(self.source.encode('utf-8')).readline):
            if token.type == tokenize.COMMENT:
                comment = token.string.strip("# ")
                initial_match = initial.match(comment)
                state_match = state.match(comment)
                loop_match = loop.match(comment)
                final_match = final.match(comment)
                if initial_match:
                    result = initial_match.group('state')
                    line = -inf                 # -inf for a precondition
                    column = -inf               # -inf for a precondition
                    yield line, column, result
                if state_match:
                    result = state_match.group('state')
                    line = token.start[0]
                    column = token.start[1]
                    yield line, column, result
                if loop_match:
                    result = loop_match.group('state')
                    line = -token.start[0]      # negative line number for a loop invariant
                    column = -token.start[1]    # negative column number for a loop invariant
                    yield line, column, result
                if final_match:
                    result = final_match.group('state')
                    line = inf                  # inf for a postcondition
                    column = inf                # inf for a postcondition
                    yield line, column, result

    def _actual_result(self, result, line, column):
        actual = None
        distanceL = inf
        distanceC = inf
        if line == -inf and column == -inf:    # precondition
            actual = next(iter(result.get_node_result(self.cfgs[''].in_node).values()))[0]
            return actual
        elif line == inf and column == inf:   # postcondition
            actual = next(iter(result.get_node_result(self.cfgs[''].out_node).values()))[0]
            return actual
        elif line < 0 and column < 0:
            for edge in self.cfgs[''].edges.values():
                if isinstance(edge, Conditional) and edge.kind == Edge.Kind.LOOP_IN:
                    currentL = abs(edge.condition.pp.line) + line
                    if currentL < distanceL:
                        states = next(iter(result.get_node_result(edge.source).values()))
                        actual = states[0]
                        distanceL = currentL
        #
        closestL = None
        for node in self.cfgs[''].nodes.values():
            states = next(iter(result.get_node_result(node).values()))
            for i, stmt in enumerate(node.stmts):
                currentL = stmt.pp.line - line
                currentC = stmt.pp.column - column
                if abs(currentL) < distanceL or (
                        abs(currentL) <= distanceL and abs(currentC) < distanceC):
                    if abs(currentL) == 1 and currentC == 0:
                        actual = states[i + 1] if currentL < 0 else states[i]
                    distanceL = abs(currentL)
                    distanceC = abs(currentC)
                    closestL = currentL
        if not actual:
            distanceL = inf
            for edge in self.cfgs[''].edges.values():
                if isinstance(edge, Conditional):
                    condition = edge.condition
                    currentL = line - abs(condition.pp.line)
                    currentC = column - abs(condition.pp.column)
                    pos = condition.pp.line > 0 and condition.pp.column > 0
                    neg = condition.pp.line < 0 and condition.pp.column < 0
                    if (closestL > 0 and pos) or (closestL < 0 and currentC > 0 and pos) or (closestL < 0 and currentC < 0 and neg):
                        if currentL >= 0 and currentL <= distanceL:
                            jumps = abs(currentC) // 4
                            _node = edge.target
                            try:
                                while jumps > 0:
                                    _node = next(iter(self.cfgs[''].successors(_node)))
                                    jumps = jumps - 1
                            except:
                                pass
                            states = next(iter(result.get_node_result(_node).values()))
                            actual = states[0]
                            distanceL = abs(currentL)
        return actual

    def check(self, result):
        comments = list(self._expected_result())
        comments.sort(key=lambda el: el[0])
        for line, column, expected in comments:
            actual = str(self._actual_result(result, line, column))
            if line == -inf:
                error = f"expected: {expected} != actual: {actual} precondition in {self.path}!"
            elif line == inf:
                error = f"expected: {expected} != actual: {actual} postcondition in {self.path}!"
            elif line < 0:
                error = f"expected: {expected} != actual: {actual} loop invariant at line {-line} in {self.path}!"
            else:
                error = f"expected: {expected} != actual: {actual} result at line {line} of {self.path}!"
            if expected != actual:
                print(error)
