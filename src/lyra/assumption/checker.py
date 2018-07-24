import os
from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Dict

from lyra.abstract_domains.assumption.assumption_domain import AssumptionState
from lyra.abstract_domains.lattice import Lattice
from lyra.assumption.error import CheckerError


class Checker(metaclass=ABCMeta):

    def __init__(self, input_path: str, error_path: str):
        self._input_path = input_path
        self._error_path = error_path

    @property
    def error_path(self):
        return self._error_path

    @property
    def input_path(self):
        return self._input_path

    def main(self, assumption: 'Lattice'):
        """Runs the input checker"""
        errors = self.check(assumption)
        self.write_errors(errors)

    @abstractmethod
    def check(self, assumption: 'Lattice') -> List[CheckerError]:
        """Performs checking of analysis result against input data"""

    @abstractmethod
    def write_errors(self, errors):
        """Writes errors found by the checker into designated file"""


class AssumptionChecker(Checker):

    def __init__(self, script_path: str, input_path: str):
        folder, name = os.path.split(script_path)
        name = name.split('.')[0]
        input_path = "{}/{}.in".format(folder, name) if input_path is None else input_path
        error_path = "{}.err".format(input)
        super().__init__(input_path, error_path)

    def check(self, assumption: 'AssumptionState.InputStack.InputLattice'):
        line_offset: Dict[int, Tuple[int, int]]

        def input_generator():
            with open(self.input_path, 'r') as file:
                start_offset, end_offset, line_number = 0, 0, 0
                for line in file:
                    input_value = line.strip()
                    end_offset = start_offset + len(input_value) - 1
                    line_offset[line_number] = (start_offset, end_offset)
                    yield line_number, input_value
                    start_offset = end_offset + 3
        assumption.check_input(input_generator())

    def write_errors(self, errors):
        pass