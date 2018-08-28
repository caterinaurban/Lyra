"""
Backward Semantics for the Assumption Analysis
==================


:Authors: Radwa Sherif and Caterina Urban
"""
from lyra.abstract_domains.state import State
from lyra.core.expressions import AttributeReference, Identifier
from lyra.core.statements import Assignment, Call
from lyra.core.types import BooleanLyraType, StringLyraType
from lyra.semantics.backward import BackwardSemantics
from lyra.semantics.semantics import DefaultSemantics


class AssumptionUserDefinedCallSemantics(BackwardSemantics):
    """Backward semantics of user-defined function/method calls."""

    # noinspection PyUnusedLocal
    def user_defined_call_semantics(self, stmt: Call, state: State):
        """Backward semantics of a user-defined function/method call.

        :param stmt: call statement to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        supported = ['isalpha', 'isalnum', 'isdecimal', 'isdigit', 'isupper', 'islower']
        if stmt.typ == BooleanLyraType() and stmt.name in supported:
            va = stmt.arguments[0].variable
            a = AttributeReference(StringLyraType(), va, Identifier(stmt.typ, stmt.name))
            state.result = {a}
            return state
        error = f"Backward semantics for call statement {stmt} not yet implemented!"
        raise NotImplementedError(error)


class AssumptionAssignmentSemantics(BackwardSemantics):
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
class AssumptionDefaultBackwardSemantics(DefaultSemantics, AssumptionUserDefinedCallSemantics,
                                         AssumptionAssignmentSemantics):
    """Default backward semantics of statements."""
    pass
