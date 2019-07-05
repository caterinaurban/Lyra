"""
Forward Semantics
=================

Lyra's internal forward semantics of statements.

:Authors: Caterina Urban
"""
from lyra.core.expressions import BinarySequenceOperation, ListDisplay
from lyra.core.types import ListLyraType
from lyra.semantics.semantics import Semantics, DefaultSemantics

from lyra.abstract_domains.state import State
from lyra.core.statements import Assignment, Call, Return

from copy import deepcopy


class ForwardSemantics(Semantics):
    """Forward semantics of statements."""

    def append_call_semantics(self, stmt: Call, state: State) -> State:
        assert len(stmt.arguments) == 2
        targets = self.semantics(stmt.arguments[0], state).result
        op = BinarySequenceOperation.Operator.Concat
        values = self.semantics(stmt.arguments[1], state).result
        rhs = set()
        for target in targets:
            for value in values:
                display = ListDisplay(ListLyraType(value.typ), [value])
                rhs.add(BinarySequenceOperation(target.typ, target, op, display))
        return state.assign(targets, rhs)


class UserDefinedCallSemantics(ForwardSemantics):
    """Forward semantics of user-defined function/method calls."""

    # noinspection PyUnusedLocal
    def user_defined_call_semantics(self, stmt: Call, state: State):
        """Forward semantics of a user-defined function/method call.

        :param stmt: call statement to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        function_name = stmt.name
        function_cfg = self._runner.names_to_cfgs[function_name]
        current_cfg = self._runner.cfg
        self._runner.cfg = function_cfg

        # map the actual parameters to the formal ones
        actual_args = stmt.arguments
        formal_args = self._runner.function_args[function_name]

        function_state = deepcopy(state)
        for (actual_arg, formal_arg) in zip(actual_args, formal_args):
            lhs = {formal_arg}
            rhs = self.semantics(actual_arg, state).result
            function_state.assign(lhs, rhs)

        extra_variables = [variable for variable in function_state.variables if variable not in formal_args]
        for variable in extra_variables:
            function_state.remove_variable(variable)

        function_result = self._runner.interpreter().analyze(function_state)
        if function_name not in self._runner.result.keys():
            self._runner.result[function_name] = [function_result]
        else:
            self._runner.result[function_name].append(function_result)
        state.result = function_state.result
        return state


class AssignmentSemantics(ForwardSemantics):
    """Forward semantics of assignments."""

    def assignment_semantics(self, stmt: Assignment, state: State) -> State:
        """Forward semantics of an assignment.

        :param stmt: assignment statement to be executed
        :param state: state before executing the assignment
        :return: state modified by the assignment
        """
        lhs = self.semantics(stmt.left, state).result    # lhs evaluation
        rhs = self.semantics(stmt.right, state).result   # rhs evaluation
        return state.assign(lhs, rhs)


class ReturnSemantics(ForwardSemantics):
    """Forward semantics of return statements."""

    # noinspection PyUnusedLocal
    def return_semantics(self, stmt: Return, state: State):
        """Forward semantics of an return statement.

        :param stmt: return statement to be executed
        :param state: state before executing the return statement
        :return: state modified by the return statement
        """

        state.result = [self.semantics(expression, state).result for expression in stmt.expressions]
        state = state.bottom()
        return state


# noinspection PyAbstractClass
class DefaultForwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics, ReturnSemantics):
    """Default forward semantics of statements."""
    pass
