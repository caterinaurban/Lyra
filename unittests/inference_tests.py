import glob
import os
import unittest
from frontend.pre_analysis import PreAnalyzer
from frontend.stmt_inferrer import *
from frontend.stubs.stubs_handler import StubsHandler


class TestInference(unittest.TestCase):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.sat = True

    @staticmethod
    def parse_comment(comment):
        assignment_text = comment[2:]  # remove the '# ' text
        variable, type_annotation = assignment_text.split(" := ")
        return variable, type_annotation

    def parse_results(self, source, solver):
        result = {}
        for line in source:
            line = line.strip()
            if not line.startswith("#"):
                continue
            if line[2:] == "unsat":
                self.sat = False
                continue
            variable, t = self.parse_comment(line)
            result[variable] = solver.resolve_annotation(ast.parse(t).body[0].value)
        return result

    def infer_file(self, path):
        """Infer a single python program

        :param path: file system path of the program to infer 
        :return: the z3 solver used to infer the program, and the global context of the program
        """
        r = open(path)
        t = ast.parse(r.read())
        r.close()

        analyzer = PreAnalyzer(t)
        stub_handler = StubsHandler(analyzer)

        config = analyzer.get_all_configurations()
        solver = z3_types.TypesSolver(config)

        context = Context()

        stub_handler.infer_all_files(context, solver, config.used_names)

        for stmt in t.body:
            infer(stmt, context, solver)

        solver.push()
        expected_result = self.parse_results(open(path), solver)

        return solver, context, expected_result

    def runTest(self):
        """Test for expressions inference"""
        solver, context, expected_result = self.infer_file(self.file_path)

        check = solver.optimize.check()
        if self.sat:
            self.assertNotEqual(check, z3_types.unsat)
        else:
            self.assertEqual(check, z3_types.unsat)
            return

        model = solver.optimize.model()
        for v in expected_result:
            self.assertIn(v, context.types_map,
                          "Expected to have variable '{}' in the global context".format(v))

            z3_type = context.types_map[v]
            self.assertEqual(model[z3_type], expected_result[v],
                             "Expected variable '{}' to have type '{}', but found '{}'".format(v,
                                                                                               expected_result[v],
                                                                                               model[z3_type]))


def suite():
    s = unittest.TestSuite()
    g = os.getcwd() + '/unittests/inference/**.py'
    for path in glob.iglob(g):
        if os.path.basename(path) != "__init__.py":
            s.addTest(TestInference(path))
    runner = unittest.TextTestRunner()
    runner.run(s)

if __name__ == '__main__':
    suite()
