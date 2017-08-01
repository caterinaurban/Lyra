import glob
import logging
import os
import unittest

from abstract_domains.numerical.octagon_domain import OctagonDomain
from core.expressions import VariableIdentifier
from engine.forward import ForwardInterpreter
from semantics.forward import DefaultForwardSemantics
from unittests.generic_tests import ResultCommentsFileTestCase

logging.basicConfig(level=logging.INFO, filename='unittests.log', filemode='w')


class OctagonTestCase(ResultCommentsFileTestCase):
    def __init__(self, source_path):
        super().__init__(source_path)
        self._source_path = source_path

    def runTest(self):
        logging.info(self)
        self.render_cfg()

        # find all variables
        variable_names = self.find_variable_names()
        int_vars = []
        list_vars = []
        for name in variable_names:
            # TODO remove this name hack when type inferences work
            if name.startswith("list"):
                typ = list
                var = VariableIdentifier(typ, name)
                list_vars.append(var)
            else:
                typ = int
                var = VariableIdentifier(typ, name)
                int_vars.append(var)

        # print(list(map(str,variables)))

        # Run Octagon numerical Analysis
        forward_interpreter = ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)
        result = forward_interpreter.analyze(OctagonDomain(int_vars + list_vars))

        # ensure all results are closed for displaying
        for node in result.nodes:
            node_result_list = result.get_node_result(node)
            for oct in node_result_list:
                oct.close()

        self.render_result_cfg(result)
        self.check_result_comments(result)


def suite():
    s = unittest.TestSuite()
    g = os.getcwd() + '/octagon/**.py'
    for path in glob.iglob(g):
        if os.path.basename(path) != "__init__.py":
            s.addTest(OctagonTestCase(path))
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
