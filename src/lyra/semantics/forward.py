"""
Forward Semantics
=================

Lyra's internal forward semantics of statements.

:Authors: Caterina Urban
"""
from typing import Union

from lyra.abstract_domains.lattice import EnvironmentMixin
from lyra.core.expressions import BinarySequenceOperation, ListDisplay, VariableIdentifier
from lyra.core.types import ListLyraType, IntegerLyraType
from lyra.engine.interpreter import Interpreter
from lyra.semantics.semantics import Semantics, DefaultSemantics

from lyra.abstract_domains.state import State
from lyra.core.statements import Assignment, Call, Return

from copy import deepcopy


class ForwardSemantics(Semantics):
    """Forward semantics of statements."""

    def append_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        assert len(stmt.arguments) == 2
        targets = self.semantics(stmt.arguments[0], state, interpreter).result
        op = BinarySequenceOperation.Operator.Concat
        values = self.semantics(stmt.arguments[1], state, interpreter).result
        rhs = set()
        for target in targets:
            for value in values:
                display = ListDisplay(ListLyraType(value.typ), [value])
                rhs.add(BinarySequenceOperation(target.typ, target, op, display))
        return state.assign(targets, rhs)


class UserDefinedCallSemantics(ForwardSemantics):
    """Forward semantics of user-defined function/method calls."""

    def user_defined_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter):
        """Forward semantics of a user-defined function/method call.

        :param stmt: call statement to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        fname, fcfg, _ = stmt.name, interpreter.cfgs[stmt.name], deepcopy(state)
        # assign function actual to formal parameters
        for formal, actual in zip(interpreter.fargs[fname], stmt.arguments):
            rhs = self.semantics(actual, state, interpreter).result
            state = state.assign({formal}, rhs)
        fresult = interpreter.analyze(fcfg, state)      # analyze the function
        fstate = fresult.get_node_result(fcfg.out_node)[state][-1]
        return state.bottom().join(deepcopy(fstate))

    def return_semantics(self, stmt: Return, state: State, interpreter: Interpreter):
        """Forward semantics of an return statement.

        :param stmt: return statement to be executed
        :param state: state before executing the return statement
        :return: state modified by the return statement
        """
        if len(stmt.values) != 1:
            error = f"Semantics for multiple arguments of {stmt} is not yet implemented!"
            raise NotImplementedError(error)
        return self.semantics(stmt.values[0], state, interpreter)


class AssignmentSemantics(ForwardSemantics):
    """Forward semantics of assignments."""

    def assignment_semantics(self, stmt: Assignment, state, interpreter) -> State:
        """Forward semantics of an assignment.

        :param stmt: assignment statement to be executed
        :param state: state before executing the assignment
        :return: state modified by the assignment
        """
        # if needed, add formal function parameters and local function variables
        if isinstance(stmt.right, Call) and stmt.right.name in interpreter.cfgs:
            # TODO: right might not be a Call but just contain a Call
            for formal in interpreter.fargs[stmt.right.name]:
                state = state.add_variable(formal).forget_variable(formal)
            for local in interpreter.cfgs[stmt.right.name].variables:
                state = state.add_variable(local).forget_variable(local)
        rhs = self.semantics(stmt.right, state, interpreter).result     # rhs evaluation
        lhs = self.semantics(stmt.left, state, interpreter).result      # lhs evaluation
        state = state.assign(lhs, rhs)
        # if needed, remove local function variables and formal function parameters
        if isinstance(stmt.right, Call) and stmt.right.name in interpreter.cfgs:
            # TODO: right might not be a Call but just contain a Call
            for local in interpreter.cfgs[stmt.right.name].variables:
                state = state.remove_variable(local)
            for formal in interpreter.fargs[stmt.right.name]:
                state = state.remove_variable(formal)
        return state


# noinspection PyAbstractClass
class DefaultForwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics):
    """Default forward semantics of statements."""
    pass
