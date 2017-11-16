import glob

from lyra.abstract_domains.numerical.interval_domain import IntervalDomain, IntervalLattice, Interval
from lyra.core.expressions import VariableIdentifier
from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics
from lyra.unittests.generic_tests import ResultCommentsFileTestCase
import unittest
import ast
import os
import logging

logging.basicConfig(level=logging.INFO, filename='unittests.log', filemode='w')


class IntervalBackwardTestCase(ResultCommentsFileTestCase):
    def __init__(self, source_path):
        super().__init__(source_path)
        self._source_path = source_path

    def runTest(self):
        logging.info(self)
        self.render_cfg()

        # find all variables
        variable_names = sorted(
            {node.id for node in ast.walk(self.ast_root) if
             isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)})
        variables = []
        for name in variable_names:
            variables.append(VariableIdentifier(int, name))

        # init all variables to bottom
        domain = IntervalDomain(variables)

        # Run Interval numerical Analysis
        backward_interpreter = BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)
        result = backward_interpreter.analyze(domain)
        self.render_result_cfg(result)
        self.check_result_comments(result)


def suite():
    s = unittest.TestSuite()
    g = os.getcwd() + '/interval/backwards/**.py'
    for path in glob.iglob(g):
        if os.path.basename(path) != "__init__.py":
            s.addTest(IntervalBackwardTestCase(path))
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
