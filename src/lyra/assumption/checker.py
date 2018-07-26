import os
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Dict, Union, Any

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
        # os.makedirs("{}/errors".format(folder), exist_ok=True)
        input_path = "{}/{}.in".format(folder, name) if input_path is None else input_path
        error_path = "{}.err".format(input_path)
        self.line_offset = None
        super().__init__(input_path, error_path)

    def check(self, assumption: 'AssumptionState.InputStack.InputLattice'):
        line_offset: Dict[int, Tuple[int, int]] = dict()

        def input_generator():
            with open(self.input_path, 'r') as file:
                start_offset, end_offset, line_number = 0, 0, 1
                for line in file:
                    input_value = line.strip()
                    end_offset = start_offset + len(input_value)
                    line_offset[line_number] = (start_offset, end_offset)
                    yield line_number, input_value
                    start_offset = end_offset + 1
                    line_number += 1

        # {'program_point': (input line number, input value)}
        pp_value: Dict[str, Tuple[int, Any]] = dict()
        # {'line_no': [errors] }
        line_errors: Dict[int, List[CheckerError]] = defaultdict(lambda: [])
        assumption.check_input(input_generator(), pp_value, line_errors)
        self.line_offset = line_offset
        self.separator = '|'
        return line_errors

    def write_errors(self, errors):
        sorted_key = sorted(errors)
        print('LINE OFSSET', self.line_offset)
        with open(self.error_path, 'w') as file:
            file.write("{}\n".format(self.separator))
            for input_line in sorted_key:
                line = []
                error_list = errors[input_line]
                line.append(str(input_line))
                line.append(str(self.line_offset[input_line][0]))
                line.append(str(self.line_offset[input_line][1]))
                err_str = self.separator.join(str(err) for err in error_list)
                line.append(err_str)
                out_line = self.separator.join([l for l in line])
                out_line += '\n'
                file.write(out_line)