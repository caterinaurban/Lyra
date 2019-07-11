"""
Forward Semantics
=================

Lyra's internal forward semantics of statements.

:Authors: Caterina Urban
"""
from lyra.core.expressions import BinarySequenceOperation, ListDisplay, VariableIdentifier
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
        self._runner.cfg = function_cfg

        # map the actual parameters to the formal ones
        actual_args = stmt.arguments
        formal_args = self._runner.function_args[function_name]

        function_state = deepcopy(state)
        for (actual_arg, formal_arg) in zip(actual_args, formal_args):
            function_state.add_variable(formal_arg)
            lhs = {formal_arg}
            rhs = self.semantics(actual_arg, state).result
            function_state.assign(lhs, rhs)

        extra_variables = [variable for variable in function_state.variables if variable not in formal_args]
        for variable in extra_variables:
            function_state.remove_variable(variable)

        # add a new variable for the result
        result_variable = VariableIdentifier(stmt.typ, function_name + "#return_result")
        function_state.add_variable(result_variable)

        function_result = self._runner.interpreter().analyze(function_state)
        if function_name not in self._runner.result.keys():
            self._runner.result[function_name] = [function_result]
        else:
            self._runner.result[function_name].append(function_result)

        function_final_state = function_result.result[function_cfg.out_node][0]
        state.result = {result_variable}
        state_copy = deepcopy(function_final_state)
        return state.join(state_copy)


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

        updated_state = state.assign(lhs, rhs)
        if isinstance(stmt.right, Call):
            # remove the result variable of the function call for user defined functions
            variables = updated_state.variables
            for variable in variables:
                if "#return_result" in variable.name:
                    updated_state.remove_variable(variable)
                    break
        return updated_state


class ReturnSemantics(ForwardSemantics):
    """Forward semantics of return statements."""

    # noinspection PyUnusedLocal
    def return_semantics(self, stmt: Return, state: State):
        """Forward semantics of an return statement.

        :param stmt: return statement to be executed
        :param state: state before executing the return statement
        :return: state modified by the return statement
        """

        # propagate the return expressions and remove all the other variables
        variables = state.variables
        result_variable = {variable for variable in variables if "#return_result" in variable.name}
        for expression in stmt.expressions:
            state.assign(result_variable, self.semantics(expression, state).result)
        for variable in variables:
            if variable not in result_variable:
                state.remove_variable(variable)
        return state


# noinspection PyAbstractClass
class DefaultForwardSemantics(DefaultSemantics, UserDefinedCallSemantics, AssignmentSemantics, ReturnSemantics):
    """Default forward semantics of statements."""
    pass
