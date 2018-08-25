"""
    Controller
    =========
    A controller class responsible for running data quality analysis, checkers and outputting results

"""
import glob
import json
import os
from abc import ABCMeta, abstractmethod
from json import JSONDecodeError

from lyra.abstract_domains.assumption.assumption_domain import JSONMixin
from lyra.abstract_domains.lattice import Lattice
from lyra.assumption.checker import Checker, AssumptionChecker
from lyra.assumption.handler import Handler, JSONHandler
from lyra.core.cfg import Basic
from lyra.engine.assumption.assumption_analysis import AssumptionAnalysis
from lyra.engine.result import AnalysisResult
from lyra.engine.runner import Runner


class Controller (metaclass= ABCMeta):

    def __init__(self, runner, handler, checker, script_path):
        self._runner = runner
        self._handler = handler
        self._checker = checker
        self._script_path = script_path

    @property
    def runner(self):
        return self._runner

    @property
    def handler(self):
        return self._handler

    @property
    def checker(self):
        return self._checker

    @property
    def script_path(self):
        return self._script_path

    @abstractmethod
    def run_analysis(self):
        """ Calls runner to run the analysis for this controller. """

    @abstractmethod
    def write_result(self, result: 'AnalysisResult'):
        """Call handler to write analysis result to a file"""

    @abstractmethod
    def read_result(self):
        """
        Calls handler to parse analysis result from a file
        :return: Result of the analysis in some data structure
        """

    @abstractmethod
    def run_checker(self, result: 'Lattice'):
        """ Run input checker associated with this controller. """

    def code_modified(self) -> bool :
        """
        Checks if
        :return:
        """
        import pickle
        import hashlib  # instead of md5

        modified = False
        db_path = os.getcwd() + '/db'
        try:
            l = pickle.load(open(db_path, 'rb'))
        except EOFError:
            l = []
        db = dict(l)
        path = self.script_path
        # this converts the hash to text
        checksum = hashlib.md5(open(path).read().encode('utf-8')).hexdigest()
        if db.get(path, None) != checksum:
            modified = True
            db[path] = checksum
        pickle.dump(db, open(db_path, "wb"))
        print('MODIFIED', modified)
        return modified

    def main(self):
        """ Run the controller """
        # if code has been modified
        if self.code_modified() or not self.handler.file_exists():
            print("Running analysis")
            result = self.run_analysis()
            print("RESULT", result)
            self.write_result(result)
        parsed_result = self.read_result()
        print("PARSED RESULT", parsed_result)
        # self.run_checker(parsed_result)


class AssumptionController(Controller):

        def __init__(self, script_path:str, input_path=None):
            args = {
                'runner': AssumptionAnalysis,
                'handler': JSONHandler(script_path),
                'checker': AssumptionChecker(script_path, input_path),
                'script_path': script_path
            }
            super().__init__(**args)
            assert self.script_path.endswith('.py'), "{} is not a python file!".format(self.script_path)


        def run_analysis(self) -> 'Lattice':
            result = self.runner().main(self.script_path)
            result = result.get_node_result(Basic(1, None))[0].stack.stack[0]
            return result

        def write_result(self, result: 'AnalysisResult'):
            with(self.script_path + '.txt', 'w') as f:
                f.write(result)
            self.handler.write_result(result)

        def read_result(self):
            return self.handler.read_result()

        def run_checker(self, result: 'JSONMixin'):
            self.checker.main(result)


if __name__ == '__main__':
    name = os.getcwd() + '/examples/tests/octagons/**.py'
    print(name)
    for path in glob.iglob(name):
        if os.path.basename(path) != "__init__.py":
            AssumptionController(path).main()

    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/cars.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/convert.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/dna.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/dna-l.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/filter.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/grades.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/lost.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/madelin1.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/mix.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/str_func.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/noinfo.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/triangle_area.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/unification.py').main()
    # AssumptionController('/home/radwa/Lyra/src/lyra/assumption/examples/tests/type+octagon+alphabet/type_merge.py').main()