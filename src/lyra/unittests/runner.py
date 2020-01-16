"""
Program Analysis - Unit Tests
=============================

:Author: Caterina Urban and Simon Wehrli
"""


import ast
import re
import tokenize
import unittest

import io
import os
from abc import ABCMeta
from math import inf

from lyra.core.cfg import Conditional, Edge
from lyra.engine.runner import Runner
from lyra.frontend.cfg_generator import ast_to_cfgs, ast_to_fargs
from lyra.visualization.graph_renderer import AnalysisResultRenderer


class TestRunner(unittest.TestCase, Runner, metaclass=ABCMeta):
    """Test analysis runner.

    Programs can be annotated with result comments::

        # INITIAL: <result>
        stmt
        # STATE: <result>
        stmt
        ...
        while ...:  # LOOP: <result>
        ...
        stmt
        # STATE: <result>
        stmt
        # FINAL: <result>

    These will be checked after the analysis.
    """

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.maxDiff = None     # to allow large diff displays in error messages
        with open(self.path, 'r', encoding="utf-8") as source:
            self.source = source.read()
            self.tree = ast.parse(self.source)
            self.cfgs = ast_to_cfgs(self.tree)
            self.fargs = ast_to_fargs(self.tree)

    def runTest(self, fname: str = ''):
        result = self.interpreter().analyze(self.cfgs[fname], self.state())
        self.render(result)
        self.check(result)

    def render(self, result):
        renderer = AnalysisResultRenderer()
        data = (self.cfgs, result)
        name = os.path.splitext(os.path.basename(self.path))[0]
        label = f"CFG with Analysis Result for {name}"
        directory = os.path.join(os.path.dirname(self.path), "graphs")
        renderer.render(data, filename=name, label=label, directory=directory, view=False)

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
                    yield line, result
                if state_match:
                    result = state_match.group('state')
                    line = token.start[0]
                    yield line, result
                if loop_match:
                    result = loop_match.group('state')
                    line = -token.start[0]      # negative line number for a loop invariant
                    yield line, result
                if final_match:
                    result = final_match.group('state')
                    line = inf                  # inf for a postcondition
                    yield line, result

    def _actual_result(self, result, line):
        actual = None
        distance = inf
        if line == -inf:    # precondition
            actual = next(iter(result.get_node_result(self.cfgs[''].in_node).values()))[0]
            return actual
        elif line == inf:   # postcondition
            actual = next(iter(result.get_node_result(self.cfgs[''].out_node).values()))[0]
            return actual
        elif line < 0:
            for edge in self.cfgs[''].edges.values():
                if isinstance(edge, Conditional) and edge.kind == Edge.Kind.LOOP_IN:
                    current = edge.condition.pp.line + line
                    if current < distance:
                        states = next(iter(result.get_node_result(edge.source).values()))
                        actual = states[0]
                        distance = current
        for node in self.cfgs[''].nodes.values():
            states = next(iter(result.get_node_result(node).values()))
            for i, stmt in enumerate(node.stmts):
                current = stmt.pp.line - line
                if abs(current) < distance:
                    actual = states[i + 1] if current < 0 else states[i]
                    distance = abs(current)
        return actual

    def check(self, result):
        comments = list(self._expected_result())
        comments.sort(key=lambda el: el[0])
        for line, expected in comments:
            actual = str(self._actual_result(result, line))
            error = f"expected != actual result at line {line} of {self.path}!"
            self.assertEqual(expected, actual, error)
