"""
Backward Semantics
==================

Lyra's internal backward semantics of statements.

:Authors: Caterina Urban
"""
from lyra.core.expressions import BinarySequenceOperation, ListDisplay
from lyra.core.types import ListLyraType
from lyra.semantics.semantics import Semantics, DefaultSemantics

from lyra.abstract_domains.state import State
from lyra.core.statements import Assignment, Call


class BackwardSemantics(Semantics):
    """Backward semantics of statements."""

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
        return state.substitute(targets, rhs)


class UserDefinedCallSemantics(BackwardSemantics):
    """Backward semantics of user-defined function/method calls."""

    # noinspection PyUnusedLocal
    def user_defined_call_semantics(self, stmt: Call, state: State):
        """Backward semantics of a user-defined function/method call.

        :param stmt: call statement to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        error = f"Backward semantics for call statement {stmt} not yet implemented!"
        raise NotImplementedError(error)


class AssignmentSemantics(BackwardSemantics):
    """Backward semantics of assignments."""

    def assignment_semantics(self, stmt: Assignment, state: State) -> State:
        """Backward semantics of an assignment.

        :param stmt: assignment statement to be executed
        :param state: state before executing the assignment
        :return: state modified by the assignment
        """
        lhs = self.semantics(stmt.left, state).result    # lhs evaluation
        rhs = self.semantics(stmt.right, state).result   # rhs evaluation
        return state.substitute(lhs, rhs)


# noinspection PyAbstractClass
class DefaultBackwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics):
    """Default backward semantics of statements."""
    pass
