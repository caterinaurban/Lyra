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
        if not isinstance(state, EnvironmentMixin):
            error = f"{state.__class__} does not support environment modifications! "
            raise ValueError(error + f"{state.__class__} must inherit from EnvironmentMixin.")
        fname, fcfg, _ = stmt.name, interpreter.cfgs[stmt.name], deepcopy(state)
        assert isinstance(state, State)
        # add formal function parameters and local function variables
        for formal in interpreter.fargs[fname]:
            state = state.add_variable(formal).forget_variable(formal)
        for local in fcfg.variables:
            state = state.add_variable(local).forget_variable(local)
        # assign function actual to formal parameters
        for formal, actual in zip(interpreter.fargs[fname], stmt.arguments):
            rhs = self.semantics(actual, state, interpreter).result
            state = state.assign({formal}, rhs)
        # (finally) analyze the function
        fresult = interpreter.analyze(fcfg, state)
        # get the resulting state
        fstate = fresult.get_node_result(fcfg.out_node)[state][-1]
        state = state.bottom().join(deepcopy(fstate))
        # remove local function variables and formal parameters
        assert isinstance(state, EnvironmentMixin) and isinstance(state, State)
        for local in fcfg.variables:
            state = state.remove_variable(local)
        for formal in interpreter.fargs[fname]:
            state = state.remove_variable(formal)
        return state

    def return_semantics(self, stmt: Return, state: State, interpreter: Interpreter):
        """Forward semantics of an return statement.

        :param stmt: return statement to be executed
        :param state: state before executing the return statement
        :return: state modified by the return statement
        """
        if len(stmt.values) != 1:
            error = f"Semantics for multiple arguments of {stmt} is not yet implemented!"
            raise NotImplementedError(error)
        if not isinstance(state, EnvironmentMixin):
            error = f"{state.__class__} does not support environment modifications! "
            raise ValueError(error + f"{state.__class__} must inherit from EnvironmentMixin.")
        assert isinstance(state, EnvironmentMixin) and isinstance(state, State)
        lhs = {variable for variable in state.variables if '#return' in variable.name}
        rhs = self.semantics(stmt.values[0], state, interpreter).result
        state = state.assign(lhs, rhs)
        state.result = lhs
        return state #self.semantics(stmt.values[0], state, interpreter)


class AssignmentSemantics(ForwardSemantics):
    """Forward semantics of assignments."""

    def assignment_semantics(self, stmt: Assignment, state, interpreter) -> State:
        """Forward semantics of an assignment.

        :param stmt: assignment statement to be executed
        :param state: state before executing the assignment
        :return: state modified by the assignment
        """
        lhs = self.semantics(stmt.left, state, interpreter).result      # lhs evaluation
        # if needed, add new function result variable
        if isinstance(stmt.right, Call) and stmt.right.name in interpreter.cfgs:
            # TODO: right might not be a Call but just contain a Call
            result = VariableIdentifier(stmt.right.typ, stmt.right.name + "#return")
            state = state.add_variable(result).forget_variable(result)
        rhs = self.semantics(stmt.right, state, interpreter).result     # rhs evaluation
        updated = state.assign(lhs, rhs)                                # assignment
        # if needed, remove function result variable
        if isinstance(stmt.right, Call) and stmt.right.name in interpreter.cfgs:
                returns = {var for var in updated.variables if '#return' in var.name}
                for variable in returns:
                    updated.remove_variable(variable)
        return updated


# noinspection PyAbstractClass
class DefaultForwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics):
    """Default forward semantics of statements."""
    pass
