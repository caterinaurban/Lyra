import ast
import glob
import logging
import os
import unittest

from lyra.engine.backward import BackwardInterpreter
from lyra.semantics.backward import DefaultBackwardSemantics

from lyra.abstract_domains.traces.traces_domain import BoolTracesState
from lyra.core.expressions import VariableIdentifier
from lyra.unittests.generic_tests import ResultCommentsFileTestCase

logging.basicConfig(level=logging.INFO, filename='unittests.log', filemode='w')


class TracesTestCase(ResultCommentsFileTestCase):
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
        variables = [VariableIdentifier(int, name) for name in variable_names]

        # run traces analysis
        backward_interpreter = BackwardInterpreter(self.cfg, DefaultBackwardSemantics(), 3)
        result = backward_interpreter.analyze(BoolTracesState(variables, True))
        self.render_result_cfg(result)


def suite():
    s = unittest.TestSuite()
    g = os.getcwd() + '/traces/**.py'
    for path in glob.iglob(g):
        if os.path.basename(path) != "__init__.py":
            s.addTest(TracesTestCase(path))
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
