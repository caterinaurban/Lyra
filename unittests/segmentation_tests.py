import glob

from abstract_domains.numerical.octagon_domain import OctagonDomain
from abstract_domains.usage.usage_domains import UsedSegmentationDomain
from core.expressions import VariableIdentifier
from engine.backward import BackwardInterpreter
from engine.forward import ForwardInterpreter
from semantics.forward import DefaultForwardSemantics
from semantics.usage.usage_semantics import UsageSemantics
from unittests.generic_tests import ResultCommentsFileTestCase
import unittest
import os
import logging

logging.basicConfig(level=logging.INFO, filename='unittests.log', filemode='w')


class SegmentationTestCase(ResultCommentsFileTestCase):
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
        list_to_len_var = {}
        for name in variable_names:
            # TODO remove this name hack when type inferences work
            if name.startswith("list"):
                typ = list
                var = VariableIdentifier(typ, name)
                list_vars.append(var)
                list_to_len_var[var] = VariableIdentifier(int, var.name + "__len")
            else:
                typ = int
                var = VariableIdentifier(typ, name)
                int_vars.append(var)
        list_len_vars = list(list_to_len_var.values())

        # print(list(map(str,variables)))

        # Run Octagonal Analysis (forward)
        forward_interpreter = ForwardInterpreter(self.cfg, DefaultForwardSemantics(), 3)
        result = forward_interpreter.analyze(OctagonDomain(int_vars + list_len_vars))

        # ensure all results are closed for displaying
        for node in result.nodes:
            node_result_list = result.get_node_result(node)
            for oct in node_result_list:
                oct.close()

        self.render_result_cfg(result, "Oct")

        # Run Usage Segmentation Analysis (backwards)
        backward_interpreter = BackwardInterpreter(self.cfg, UsageSemantics(), 3)
        result = backward_interpreter.analyze(
            UsedSegmentationDomain(int_vars, list_vars, list_len_vars, list_to_len_var, result))

        self.render_result_cfg(result, "Seg")
        self.check_result_comments(result)


def suite():
    s = unittest.TestSuite()
    g = os.getcwd() + '/segmentation/**.py'
    for path in glob.iglob(g):
        if os.path.basename(path) != "__init__.py":
            s.addTest(SegmentationTestCase(path))
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
