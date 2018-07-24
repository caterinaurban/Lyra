"""
    I/O interfacing classes.
===========================

:Authors: Radwa Sherif Abdelbar
"""
import os
import json

from abc import ABCMeta, abstractmethod

from lyra.abstract_domains.assumption.assumption_domain import AssumptionState
from lyra.core.cfg import Basic
from lyra.core.utils import copy_docstring
from lyra.engine.result import AnalysisResult


class Handler (metaclass=ABCMeta):
    """
        File I/O interface for the assumptions of a program. Reads and write analysis result from file.
    """

    def __init__(self):
        """

        :param extensionless_path: path to the python script being analyzed without .py extension
        """
        self._assumption_file = None

    @property
    def assumption_file(self):
        """
        Path of the file to which the assumptions are written.
        :return: Canonical path to program assumptions file.
        """
        return self._assumption_file

    def file_exists(self):
        """
        Checks whether assumptions for the current program have been written to a file or not.
        :return:
        """
        return os.path.isfile(self.assumption_file)

    @abstractmethod
    def write_result(self, result: 'AnalysisResult'):
        """Write analysis result to file"""

    @abstractmethod
    def read_result(self):
        """Read analysis result from file into data structure"""


class JSONHandler(Handler):

    def __init__(self, script_path: str):
        super().__init__()
        folder, script = os.path.split(script_path)
        script_name = script.split('.')[0]
        os.makedirs("{}/json".format(folder), exist_ok=True)
        self._assumption_file = "{}/json/{}.json".format(folder, script_name)

    @copy_docstring(Handler.write_result)
    def write_result(self, result: 'AssumptionState.InputStack.InputLattice'):
        js = result.to_json()
        with open(self.assumption_file, 'w') as outfile:
            json.dump(js, outfile, indent=4)

    @copy_docstring(Handler.read_result)
    def read_result(self):
        with open(self.assumption_file, 'r') as infile:
            js = json.load(infile)
        return AssumptionState.InputStack.InputLattice.from_json(js)
