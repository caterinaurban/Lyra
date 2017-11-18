from lyra.semantics.semantics import Semantics, DefaultSemantics

from lyra.abstract_domains.state import State
from lyra.core.statements import VariableAccess, Assignment, Call


class BackwardSemantics(Semantics):
    """Backward semantics of statements."""
    pass


class UserDefinedCallSemantics(BackwardSemantics):
    """Backward semantics of user-defined function/method calls."""

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
        if isinstance(stmt.left, VariableAccess):
            return state.substitute_variable(lhs, rhs)
        error = f"Backward semantics for assignment {stmt} not yet implemented!"
        raise NotImplementedError(error)


# noinspection PyAbstractClass
class DefaultBackwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics):
    """Default backward semantics of statements."""
    pass
