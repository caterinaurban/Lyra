import glob
import logging
import os
import unittest

from lyra.core.expressions import VariableIdentifier
from lyra.engine.backward import BackwardInterpreter

from lyra.abstract_domains.usage.stack import UsedStack
from lyra.engine.usage.usage_analysis import UsageAnalysis
from lyra.semantics.usage.usage_semantics import UsageSemantics
from lyra.unittests.generic_tests import ResultCommentsFileTestCase

logging.basicConfig(level=logging.INFO, filename='unittests.log', filemode='w')


class UsageTestCase(ResultCommentsFileTestCase):
    def __init__(self, path):
        super().__init__(path)
        self._source_path = path

    def runTest(self):
        logging.info(self)
        self.render_cfg()

        analysis = UsageAnalysis()
        analysis.cfg = self.cfg
        result = analysis.run()
        self.render_result_cfg(result)
        self.check_result_comments(result)


def suite():
    s = unittest.TestSuite()
    g = os.getcwd() + '/usage/**.py'
    for path in glob.iglob(g):
        if os.path.basename(path) != "__init__.py":
            s.addTest(UsageTestCase(path))
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
