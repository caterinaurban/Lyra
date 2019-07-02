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
from lyra.core.statements import Assignment, Call


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
        function_cfg = self._runner.cfgs[function_name]
        current_cfg = self._runner.cfg
        self._runner.cfg = function_cfg

        # map the actual parameters to the formal ones
        actual_args = stmt.arguments
        formal_args = self._runner.function_args[function_name]

        old_state = state
        for (actual_arg, formal_arg) in zip(actual_args, formal_args):
            lhs = {formal_arg}
            rhs = self.semantics(actual_arg, old_state).result
            state.assign(lhs, rhs)

        function_result = self._runner.interpreter().analyze(state)
        self._runner.partial_result.update(function_result.result)
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


# noinspection PyAbstractClass
class DefaultForwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics):
    """Default forward semantics of statements."""
    pass
