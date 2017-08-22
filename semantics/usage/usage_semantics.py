from typing import List

from abstract_domains.state import State
from core.expressions import ListInput, VariableIdentifier
from core.statements import Call, VariableAccess
from semantics.backward import DefaultBackwardSemantics
from semantics.forward import DefaultForwardSemantics


class UsageOctagonSemantics(DefaultForwardSemantics):
    def user_defined_call_semantics(self, stmt: Call, state: State) -> State:
        raise NotImplementedError("Usage semantics for call statement {} not yet implemented!".format(stmt))

    def list_call_semantics(self, stmt: Call, state: State) -> State:
        if len(stmt.arguments) != 1:
            raise NotImplementedError(f"No semantics implemented for the multiple arguments to list()")

        if str(stmt.arguments[0]) != "map(int, split(input()))":
            raise NotImplementedError(f"The only supported argument to list() is 'map(int, split(input()))'")

        state.result = {ListInput(List[int])}
        return state

    def len_call_semantics(self, stmt: Call, state: State) -> State:
        if len(stmt.arguments) != 1:
            raise NotImplementedError(f"No semantics implemented for the multiple arguments to len()")

        arg = stmt.arguments[0]
        if not isinstance(arg, VariableAccess):
            raise NotImplementedError(f"The only supported argument to len() is a variable identifier")
        var = arg.var
        if var.typ != list:
            raise NotImplementedError(f"The variable identifier passed to len() must have type list")

        state.result = {VariableIdentifier(int, var.name + "__len")}
        return state


class UsageSemantics(DefaultBackwardSemantics):
    def user_defined_call_semantics(self, stmt: Call, state: State) -> State:
        raise NotImplementedError("Usage semantics for call statement {} not yet implemented!".format(stmt))

    def list_call_semantics(self, stmt: Call, state: State) -> State:
        if len(stmt.arguments) != 1:
            raise NotImplementedError(f"No semantics implemented for the multiple arguments to list()")

        if str(stmt.arguments[0]) != "map(int, split(input()))":
            raise NotImplementedError(f"The only supported argument to list() is 'map(int, split(input()))'")

        state.result = {ListInput(List[int])}
        return state

    def len_call_semantics(self, stmt: Call, state: State) -> State:
        if len(stmt.arguments) != 1:
            raise NotImplementedError(f"No semantics implemented for the multiple arguments to len()")

        arg = stmt.arguments[0]
        if not isinstance(arg, VariableAccess):
            raise NotImplementedError(f"The only supported argument to len() is a variable identifier")
        var = arg.var
        if var.typ != list:
            raise NotImplementedError(f"The variable identifier passed to len() must have type list")

        state.result = {VariableIdentifier(int, var.name + "__len")}
        return state
