import unittest

from abstract_domains.numerical.linear_forms import VarForm
from unittests.generic_tests import ExpressionTreeTestCase


class TestVarForm(ExpressionTreeTestCase):
    def __init__(self, name, source, expected_result):
        super().__init__(source, f"VarForm - {name}")
        self._expected_result = expected_result

    def runTest(self):
        result = super().runTest()

        result_store = result.get_node_result(self.cfg.nodes[2])[1]
        right_expr = result_store.store[self.variables['a']]

        try:
            form = VarForm.from_expression(right_expr)
        except ValueError:
            form = "INVALID FORM"

        self.assertEqual(str(form), self._expected_result, self.source)


def suite():
    s = unittest.TestSuite()
    s.addTest(TestVarForm("simple", """a = b * (2+5)""", "INVALID FORM"))
    s.addTest(TestVarForm("simple", """a = (2+5) * b""", "INVALID FORM"))
    s.addTest(TestVarForm("simple", """a = b + (2+5)""", "+b + [7,7]"))
    s.addTest(TestVarForm("simple", """a = (2+5) + b""", "+b + [7,7]"))
    s.addTest(TestVarForm("simple", """a = -b + 2*(2+5)""", "-b + [14,14]"))
    s.addTest(TestVarForm("simple", """a = 2*(2+5) -b""", "-b + [14,14]"))
    s.addTest(TestVarForm("simple", """a = b - (2+5)""", "+b + [-7,-7]"))
    s.addTest(TestVarForm("simple", """a = -(2+5) + b""", "+b + [-7,-7]"))
    s.addTest(TestVarForm("simple", """a = b""", "+b"))
    runner = unittest.TextTestRunner()
    runner.run(s)


if __name__ == '__main__':
    suite()
