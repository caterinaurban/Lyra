import os
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Dict, Union, Any

from lyra.abstract_domains.assumption.assumption_domain import AssumptionState
from lyra.abstract_domains.lattice import Lattice
from lyra.assumption.error import CheckerError, RelationalError, DependencyError


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
        self.separator = '|'
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
        return line_errors

    def write_errors(self, errors):

        def do(errors, line_number):
            messages = []
            message = ';'.join([err.message for err in errors if isinstance(err, RelationalError)])
            if len(message) > 0:
                message = "Expected condition(s): {}".format(message)
                messages.append(message)

            source_lines = set([str(err.source_line) for err in set(errors) if isinstance(err, DependencyError) and err.source_line != line_number])
            message = ', '.join(source_lines)
            if len(message) > 0:
                message = "This line depends on previous error value on line(s): {}".format(message)
                messages.append(message)

            message = '. '.join([err.message for err in errors if not (isinstance(err, RelationalError) or isinstance(err, DependencyError))])
            if len(message) > 0:
                messages.append(message)

            return '. '.join([msg for msg in messages])

        sorted_key = sorted(errors)
        with open(self.error_path, 'w') as file:
            if len(errors) > 0:
                file.write("{}\n".format(self.separator))
            else:
                file.write('')
            # print("-----------ERROR FILE----------")
            for input_line in sorted_key:
                line = []
                error_list = errors[input_line]
                line.append(str(input_line))
                line.append(str(self.line_offset[input_line][0]))
                line.append(str(self.line_offset[input_line][1]))
                line.append(do(error_list, input_line))
                out_line = self.separator.join([l for l in line])
                out_line += '\n'
                # print(out_line)
                file.write(out_line)
            # print("-----------END ERROR FILE--------")