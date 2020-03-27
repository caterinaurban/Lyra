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

    def check(self, result):
        comments = list(self._expected_result())
        comments.sort(key=lambda el: el[0])
        for line, column, expected in comments:
            actual = str(self._actual_result(result, line, column))
            if line == -inf:
                error = f"expected != actual precondition in {self.path}!"
            elif line == inf:
                error = f"expected != actual postcondition in {self.path}!"
            elif line < 0:
                error = f"expected != actual loop invariant at line {-line} in {self.path}!"
            else:
                error = f"expected != actual result at line {line} of {self.path}!"
            self.assertEqual(expected, actual, error)
