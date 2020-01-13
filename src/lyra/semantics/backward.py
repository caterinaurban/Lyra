"""
Backward Semantics
==================

Lyra's internal backward semantics of statements.

:Authors: Caterina Urban
"""
from lyra.core.expressions import BinarySequenceOperation, ListDisplay, VariableIdentifier
from lyra.core.types import ListLyraType
from lyra.semantics.semantics import Semantics, DefaultSemantics

from lyra.abstract_domains.state import State
from lyra.core.statements import Assignment, Call, Return

from copy import deepcopy


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
        function_name = stmt.name
        function_cfg = self._runner.names_to_cfgs[function_name]
        self._runner.cfg = function_cfg

        function_state = deepcopy(state)
        local_variables = self._runner.variables

        # add the local variables and set them to top
        for local_variable in local_variables:
            function_state.add_variable(local_variable)
            function_state.forget_variable(local_variable)

        extra_variables = [variable for variable in function_state.variables if
                           function_name + "#" not in variable.name]
        for variable in extra_variables:
            function_state.remove_variable(variable)

        function_result = self._runner.interpreter().analyze(function_state)
        if function_name not in self._runner.result.keys():
            self._runner.result[function_name] = [function_result]
        else:
            self._runner.result[function_name].append(function_result)

        function_final_state = function_result.result[function_cfg.in_node][0]
        state_copy = deepcopy(function_final_state)

        # map the actual parameters to the formal ones
        actual_args = stmt.arguments
        formal_args = self._runner.function_args[function_name]

        state = state.join(state_copy)
        for (actual_arg, local_variable) in zip(actual_args, formal_args):
            lhs = {local_variable}
            rhs = self.semantics(actual_arg, state).result
            state.substitute(lhs, rhs)

        result_variable = None
        for variable in state.variables:
            if "#return_result" in variable.name:
                result_variable = variable
                break
        state.result = {result_variable}

        # remove all the local variables of the function (except the return result)
        for variable in local_variables:
            state.remove_variable(variable)
        return state




class AssignmentSemantics(BackwardSemantics):
    """Backward semantics of assignments."""

    def assignment_semantics(self, stmt: Assignment, state: State) -> State:
        """Backward semantics of an assignment.

        :param stmt: assignment statement to be executed
        :param state: state before executing the assignment
        :return: state modified by the assignment
        """
        lhs = self.semantics(stmt.left, state).result    # lhs evaluation

        result_variable = None

        if isinstance(stmt.right, Call):
            function_name = stmt.right.name
            if function_name in self._runner.cfgs.keys():
                # add a new variable for the result of a user defined function
                result_variable = VariableIdentifier(stmt.right.typ, function_name + "#return_result")
                state.add_variable(result_variable)
                state.assign({result_variable}, lhs)

        rhs = self.semantics(stmt.right, state).result   # rhs evaluation
        updated_state = state.substitute(lhs, rhs)

        if result_variable is not None:
            # remove the result variable for a user defined function
            state.remove_variable(result_variable)
        return updated_state


class ReturnSemantics(BackwardSemantics):
    """Backward semantics of return statements."""

    # noinspection PyUnusedLocal
    def return_semantics(self, stmt: Return, state: State):
        """Backward semantics of an return statement.

        :param stmt: return statement to be executed
        :param state: state before executing the return statement
        :return: state modified by the return statement
        """

        # propagate the return result to the return expressions
        variables = state.variables
        result_variable = {variable for variable in variables if "#return_result" in variable.name}
        for expression in stmt.expressions:
            state.assign(self.semantics(expression, state).result, result_variable)
        return state


# noinspection PyAbstractClass
class DefaultBackwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics, ReturnSemantics):
    """Default backward semantics of statements."""
    pass
