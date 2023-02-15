from abc import ABCMeta

from lyra.abstract_domains.state import State
from lyra.core.statements import Call
from lyra.engine.interpreter import Interpreter
from lyra.semantics.semantics import CallSemantics, DefaultSemantics


class PandasCallSemantics(CallSemantics, metaclass=ABCMeta):
    """Semantics of Pandas library calls."""

    def drop_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'drop'.

        :param stmt: call to 'read_csv' to be executed
        :param state: state before analyzing the call statement
        :param interpreter: interpreter for resolving user-defined calls
        :return: state modified by the call statement
        """

    def head_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'head'.

        :param stmt: call to 'read_csv' to be executed
        :param state: state before analyzing the call statement
        :param interpreter: interpreter for resolving user-defined calls
        :return: state modified by the call statement
        """

    def read_csv_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'read_csv'.

        :param stmt: call to 'read_csv' to be executed
        :param state: state before analyzing the call statement
        :param interpreter: interpreter for resolving user-defined calls
        :return: state modified by the call statement
        """




class DefaultPandasSemantics(DefaultSemantics, PandasCallSemantics, metaclass=ABCMeta):
    """Default semantics of statements with support for Pandas library calls.

    The semantics is independent of the direction (forward/backward) of the analysis."""
    pass
