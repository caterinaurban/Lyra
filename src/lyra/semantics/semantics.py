"""
Semantics
=========

Lyra's internal semantics of statements.

:Authors: Caterina Urban and Simon Wehrli
"""


import itertools
import re
from copy import deepcopy

from lyra.abstract_domains.state import State
from lyra.core.expressions import BinaryArithmeticOperation, Subscription, Slicing, \
    LengthIdentifier, VariableIdentifier, Range, Expression, BinarySequenceOperation, CastOperation
from lyra.core.expressions import BinaryBooleanOperation, Input, TupleDisplay, ListDisplay, \
    Literal, SetDisplay, DictDisplay, Items, Keys, Values
from lyra.core.expressions import BinaryOperation, BinaryComparisonOperation
from lyra.core.expressions import UnaryArithmeticOperation, UnaryBooleanOperation
from lyra.core.expressions import UnaryOperation
from lyra.core.expressions import AttributeReference
from lyra.core.statements import Statement, VariableAccess, LiteralEvaluation, Call, \
    TupleDisplayAccess, ListDisplayAccess, SetDisplayAccess, DictDisplayAccess, \
    SubscriptionAccess, SlicingAccess, \
    AttributeAccess
from lyra.core.types import LyraType, BooleanLyraType, IntegerLyraType, FloatLyraType, \
    StringLyraType, TupleLyraType, ListLyraType, SetLyraType, DictLyraType
from lyra.engine.interpreter import Interpreter

_first1 = re.compile(r'(.)([A-Z][a-z]+)')
_all2 = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case

    :param name: name in CamelCase
    :return: name in snake_case
    """
    subbed = _first1.sub(r'\1_\2', name)
    return _all2.sub(r'\1_\2', subbed).lower()


class Semantics:
    """Semantics of statements.

    The semantics is independent of the direction (forward/backward) of the analysis.
    """

    def semantics(self, stmt: Statement, state: State, interpreter: Interpreter) -> State:
        """Semantics of a statement.

        :param stmt: statement to be executed
        :param state: state before executing the statement
        :return: state modified by the statement execution
        """
        name = '{}_semantics'.format(camel_to_snake(stmt.__class__.__name__))
        if hasattr(self, name):
            return getattr(self, name)(stmt, state, interpreter)
        error = f"Semantics for statement {stmt} of type {type(stmt)} not yet implemented! "
        raise NotImplementedError(error + f"You must provide method {name}(...)")

    def import_semantics(self, stmt: Statement, state: State, interpreter: Interpreter) -> State:
        """Semantics of an import statement."""
        return state


class ExpressionSemantics(Semantics):
    """Semantics of expression evaluations and accesses."""

    # noinspection PyMethodMayBeStatic
    def literal_evaluation_semantics(self, stmt: LiteralEvaluation, state, interpreter) -> State:
        """Semantics of a literal evaluation.

        :param stmt: literal evaluation statement to be executed
        :param state: state before executing the literal evaluation
        :return: stated modified by the literal evaluation
        """
        state.result = {stmt.literal}
        return state

    # noinspection PyMethodMayBeStatic
    def variable_access_semantics(self, stmt: VariableAccess, state, interpreter) -> State:
        """Semantics of a variable access.

        :param stmt: variable access statement to be executed
        :param state: state before executing the variable access
        :return: state modified by the variable access
        """
        state.result = {stmt.variable}
        return state

    def list_display_access_semantics(self, stmt: ListDisplayAccess, state, interpreter) -> State:
        """Semantics of a list display access.

        :param stmt: list display access statement to be executed
        :param state: state before executing the list display access
        :return: state modified by the list display access
        """
        items = [self.semantics(item, state, interpreter).result for item in stmt.items]
        result = set()
        for combination in itertools.product(*items):
            display = ListDisplay(stmt.typ, list(combination))
            result.add(display)
        state.result = result
        return state

    def tuple_display_access_semantics(self, stmt: TupleDisplayAccess, state, interpreter) -> State:
        """Semantics of a tuple display access.

                :param stmt: tuple display access statement to be executed
                :param state: state before executing the tuple display access
                :return: state modified by the tuple display access
                """
        items = [self.semantics(item, state, interpreter).result for item in stmt.items]
        result = set()
        for combination in itertools.product(*items):
            display = TupleDisplay(stmt.typ, list(combination))
            result.add(display)
        state.result = result
        return state

    def set_display_access_semantics(self, stmt: SetDisplayAccess, state, interpreter) -> State:
        """Semantics of a set display access.

        :param stmt: set display access statement to be executed
        :param state: state before executing the set display access
        :return: state modified by the set display access
        """
        items = [self.semantics(item, state, interpreter).result for item in stmt.items]
        result = set()
        for combination in itertools.product(*items):
            display = SetDisplay(stmt.typ, list(combination))
            result.add(display)
        state.result = result
        return state

    def dict_display_access_semantics(self, stmt: DictDisplayAccess, state, interpreter) -> State:
        """Semantics of a list display access.

        :param stmt: dictionary display access statement to be executed
        :param state: state before executing the dictionary display access
        :return: state modified by the dictionary display access
        """
        keys = [self.semantics(k, state, interpreter).result for k in stmt.keys]
        values = [self.semantics(v, state, interpreter).result for v in stmt.values]
        result = set()
        if keys:  # not empty List[Set[Expression]]
            for combination in itertools.product(*map(itertools.product, keys, values)):
                unzip = list(zip(*combination))  # to create two separate lists for keys and values
                display = DictDisplay(stmt.typ, list(unzip[0]), list(unzip[1]))
                result.add(display)
        else:
            result.add(DictDisplay(stmt.typ, list(), list()))
        state.result = result
        return state

    def subscription_access_semantics(self, stmt: SubscriptionAccess, state, interpreter) -> State:
        """Semantics of a subscription access.

        :param stmt: subscription access statement to be executed
        :param state: state before executing the subscription access
        :return: state modified by the subscription access
        """
        target = self.semantics(stmt.target, state, interpreter).result
        key = self.semantics(stmt.key, state, interpreter).result
        result = set()
        for primary, index in itertools.product(target, key):
            if isinstance(primary.typ, StringLyraType):
                subscription = Subscription(primary.typ, primary, index)
                result.add(subscription)
            elif isinstance(primary.typ, (ListLyraType, SetLyraType)):
                subscription = Subscription(primary.typ.typ, primary, index)
                result.add(subscription)
            elif isinstance(primary.typ, DictLyraType):
                subscription = Subscription(primary.typ.val_typ, primary, index)
                result.add(subscription)
            elif isinstance(primary.typ, TupleLyraType):
                if not isinstance(index, Literal):
                    error = f"Semantics for {primary}[{index}] is not yet implemented!"
                    raise NotImplementedError(error)
                subscription = Subscription(primary.typ.typs[int(index.val)], primary, index)
                result.add(subscription)
            else:
                error = f"Semantics for subscription of {primary} is not yet implemented!"
                raise NotImplementedError(error)
        state.result = result
        return state

    def slicing_access_semantics(self, stmt: SlicingAccess, state, interpreter) -> State:
        """Semantics of a slicing access.

        :param stmt: slicing access statement to be executed
        :param state: state before executing the slicing access
        :return: state modified by the slicing access
        """
        target = self.semantics(stmt.target, state, interpreter).result
        lower = self.semantics(stmt.lower, state, interpreter).result if stmt.lower else {None}
        upper = self.semantics(stmt.upper, state, interpreter).result if stmt.upper else {None}
        stride = self.semantics(stmt.stride, state, interpreter).result if stmt.stride else {None}
        result = set()
        for primary, start, stop, step in itertools.product(target, lower, upper, stride):
            slicing = Slicing(primary.typ, primary, start, stop, step)
            result.add(slicing)
        state.result = result
        return state

    def attribute_access_semantics(self, stmt: AttributeAccess, state, interpreter) -> State:
        """Semantics of an attribute access.
        """
        # This simply transforms the statement into an expression (or
        # expressions), and does not depend on the attribute name. The behavior
        # that depends on the attribute name is therefore delegated to whoever
        # handles the AttributeReference expression.
        target = self.semantics(stmt.target, state, interpreter).result
        attr = stmt.attr
        state.result = {AttributeReference(stmt.typ, t, attr) for t in target}
        return state


class CallSemantics(Semantics):
    """Semantics of function/method calls."""

    def call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a function/method call.

        :param stmt: call statement to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        name = '{}_call_semantics'.format(stmt.name)
        if hasattr(self, name):
            return getattr(self, name)(stmt, state, interpreter)
        return getattr(self, 'user_defined_call_semantics')(stmt, state, interpreter)


class BuiltInCallSemantics(CallSemantics):
    """Semantics of built-in function/method calls."""

    def _cast_call_semantics(self, stmt: Call, state, interpreter, typ: LyraType) -> State:
        """Semantics of a call to 'int', 'bool', or 'float'.

        :param stmt: call to 'int', 'bool', 'float', or 'str' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if len(stmt.arguments) != 1:
            error = f"Semantics for multiple arguments of {stmt.name} is not yet implemented!"
            raise NotImplementedError(error)
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for expression in argument:
            if isinstance(expression, Input):
                result.add(Input(typ))
            elif isinstance(expression, Literal):
                result.add(Literal(typ, expression.val))
            else:
                result.add(CastOperation(typ, expression))
        state.result = result
        return state

    def bool_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'bool'.

        :param stmt: call to 'bool' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._cast_call_semantics(stmt, state, interpreter, BooleanLyraType())

    def int_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'int'.

        :param stmt: call to 'int' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._cast_call_semantics(stmt, state, interpreter, IntegerLyraType())

    def float_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'float'.

        :param stmt: call to 'float' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._cast_call_semantics(stmt, state, interpreter, FloatLyraType())

    def str_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'str'.

        :param stmt: call to 'str' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._cast_call_semantics(stmt, state, interpreter, StringLyraType())

    def list_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'list'.

        :param stmt: call to 'list' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            state.result = {ListDisplay(stmt.typ, list())}
            return state
        assert len(stmt.arguments) == 1  # exactly one argument is expected
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for expression in argument:
            if isinstance(expression.typ, StringLyraType):
                typ = ListLyraType(expression.typ)
                result.add(CastOperation(typ, expression))
            elif isinstance(expression.typ, ListLyraType):
                result.add(expression)
            elif isinstance(expression.typ, TupleLyraType):
                if all(typ == expression.typ.typs[0] for typ in expression.typ.typs):
                    typ = ListLyraType(expression.typ.typs[0])
                    result.add(CastOperation(typ, expression))
                else:
                    error = f"Cast to list of {expression} is not yet implemented!"
                    raise NotImplementedError(error)
            elif isinstance(expression.typ, SetLyraType):
                typ = ListLyraType(expression.typ.typ)
                result.add(CastOperation(typ, expression))
            elif isinstance(expression.typ, DictLyraType):
                typ = ListLyraType(expression.typ.key_typ)
                result.add(CastOperation(typ, expression))
            else:
                error = f"Cast to list of expression {expression} with unexpected type!"
                raise ValueError(error)
        state.result = result
        return state

    def set_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'set'.

        :param stmt: call to 'set' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            state.result = {SetDisplay(stmt.typ, list())}
            return state
        assert len(stmt.arguments) == 1  # exactly one argument is expected
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for expression in argument:
            if isinstance(expression.typ, StringLyraType):
                typ = SetLyraType(expression.typ)
                result.add(CastOperation(typ, expression))
            elif isinstance(expression.typ, ListLyraType):
                typ = SetLyraType(expression.typ.typ)
                result.add(CastOperation(typ, expression))
            elif isinstance(expression.typ, TupleLyraType):
                if all(typ == expression.typ.typs[0] for typ in expression.typ.typs):
                    typ = SetLyraType(expression.typ.typs[0])
                    result.add(CastOperation(typ, expression))
                else:
                    error = f"Cast to list of {expression} is not yet implemented!"
                    raise NotImplementedError(error)
            elif isinstance(expression.typ, SetLyraType):
                result.add(expression)
            elif isinstance(expression.typ, DictLyraType):
                typ = SetLyraType(expression.typ.key_typ)
                result.add(CastOperation(typ, expression))
            else:
                error = f"Cast to list of expression {expression} with unexpected type!"
                raise ValueError(error)
        state.result = result
        return state

    def tuple_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'tuple'.

        :param stmt: call to 'tuple' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            state.result = {TupleDisplay(stmt.typ, list())}
            return state
        assert len(stmt.arguments) == 1  # exactly one argument is expected
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for expression in argument:
            if isinstance(expression.typ, StringLyraType):
                if isinstance(expression, Literal):
                    typs = [deepcopy(expression.typ) for _ in range(len(expression.val))]
                    typ = TupleLyraType(typs)
                    result.add(CastOperation(typ, expression))
                else:
                    error = f"Cast to tuple of {expression} is not yet implemented!"
                    raise NotImplementedError(error)
            elif isinstance(expression.typ, (ListLyraType, SetLyraType)):
                if isinstance(expression, ListDisplay):
                    typs = [deepcopy(expression.typ.typ) for _ in range(len(expression.items))]
                    typ = TupleLyraType(typs)
                    result.add(CastOperation(typ, expression))
                else:
                    error = f"Cast to tuple of {expression} is not yet implemented!"
                    raise NotImplementedError(error)
            elif isinstance(expression.typ, TupleLyraType):
                result.add(expression)
            elif isinstance(expression.typ, DictLyraType):
                if isinstance(expression, DictDisplay):
                    typs = [deepcopy(expression.typ.key_typ) for _ in range(len(expression.keys))]
                    typ = TupleLyraType(typs)
                    result.add(CastOperation(typ, expression))
                else:
                    error = f"Cast to tuple of {expression} is not yet implemented!"
                    raise NotImplementedError(error)
            else:
                error = f"Cast to list of expression {expression} with unexpected type!"
                raise ValueError(error)
        state.result = result
        return state

    def dict_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'dict'.

        :param stmt: call to 'dict' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            assert isinstance(stmt.typ, DictLyraType)
            state.result = {DictDisplay(stmt.typ, list(), list())}
            return state
        raise NotImplementedError(f"Semantics for {stmt} is not yet implemented!")

    def len_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'len'.

        :param stmt: call to 'len' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        assert len(stmt.arguments) == 1  # unary operations have exactly one argument
        argument = stmt.arguments[0]
        if isinstance(argument, VariableAccess):
            variable = argument.variable
            state.result = {LengthIdentifier(variable)}
            return state
        elif isinstance(argument, ListDisplayAccess):
            items = [self.semantics(item, state, interpreter).result for item in argument.items]
            result = set()
            for combination in itertools.product(*items):
                display = ListDisplay(argument.typ, list(combination))
                result.add(LengthIdentifier(display))
            state.result = result
            return state
        elif isinstance(argument, TupleDisplayAccess):
            items = [self.semantics(item, state, interpreter).result for item in argument.items]
            result = set()
            for combination in itertools.product(*items):
                display = TupleDisplay(argument.typ, list(combination))
                result.add(LengthIdentifier(display))
            state.result = result
            return state
        elif isinstance(argument, SetDisplayAccess):
            items = [self.semantics(item, state, interpreter).result for item in argument.items]
            result = set()
            for combination in itertools.product(*items):
                display = SetDisplay(argument.typ, list(combination))
                result.add(LengthIdentifier(display))
            state.result = result
            return state
        elif isinstance(argument, DictDisplayAccess):
            keys = [self.semantics(k, state, interpreter).result for k in argument.keys]
            values = [self.semantics(v, state, interpreter).result for v in argument.values]
            result = set()
            if keys:  # not empty List[Set[Expression]]
                for combination in itertools.product(*map(itertools.product, keys, values)):
                    unzip = list(zip(*combination))
                    display = DictDisplay(argument.typ, list(unzip[0]), list(unzip[1]))
                    result.add(LengthIdentifier(display))
            else:
                result.add(LengthIdentifier(DictDisplay(argument.typ, list(), list())))
            state.result = result
            return state
        error = f"Semantics for length of {argument} is not yet implemented!"
        raise NotImplementedError(error)

    def split_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        if len(stmt.arguments) != 1:
            error = f"Semantics for multiple arguments of {stmt.name} is not yet implemented!"
            raise NotImplementedError(error)
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for arg in argument:
            assert isinstance(arg, Expression)
            if not isinstance(arg.typ, StringLyraType):
                error = f"Call to {stmt.name} of argument with unexpected type!"
                raise ValueError(error)
            typ = ListLyraType(StringLyraType())
            if isinstance(arg, Literal):                # "a b c".split() -> ["a", "b", "c"]
                items = [Literal(StringLyraType(), val) for val in arg.val.split()]
                result.add(ListDisplay(typ, items))
                continue
            elif isinstance(arg, VariableIdentifier):   # TODO: x.split()
                result.add(VariableIdentifier(typ, arg.name))
                continue
            elif isinstance(arg, Input):                # input().split()
                result.add(Input(typ))
                continue
            error = f"Call to {stmt.name} of unexpected argument {arg}!"
            raise ValueError(error)
        state.result = result
        return state

    def strip_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        if len(stmt.arguments) != 1:
            error = f"Semantics for multiple arguments of {stmt.name} is not yet implemented!"
            raise NotImplementedError(error)
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for arg in argument:
            assert isinstance(arg, Expression)
            if not isinstance(arg.typ, StringLyraType):
                error = f"Call to {stmt.name} of argument with unexpected type!"
                raise ValueError(error)
            typ = StringLyraType()
            if isinstance(arg, Input):                  # input().strip()
                result.add(Input(typ))
                continue
            elif isinstance(arg, VariableIdentifier):   # x.strip()
                result.add(VariableIdentifier(typ, arg.name))
                continue
            elif isinstance(arg, Subscription):         # x[i].strip()
                result.add(Subscription(typ, arg.target, arg.key))
                continue
            error = f"Call to {stmt.name} of unexpected argument {arg}!"
            raise ValueError(error)
        state.result = result
        return state

    def lstrip_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        return self.strip_call_semantics(stmt, state, interpreter)

    def rstrip_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        return self.strip_call_semantics(stmt, state, interpreter)

    # noinspection PyMethodMayBeStatic
    def input_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a calls to 'input'.

        :param stmt: call to 'input' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        state.result = {Input(stmt.typ)}
        return state

    def print_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'print'.

        :param stmt: call to 'print' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if len(stmt.arguments) != 1:
            error = f"Semantics for multiple arguments of {stmt.name} is not yet implemented!"
            raise NotImplementedError(error)
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        return state.output(argument)

    def range_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        result = set()
        if len(stmt.arguments) == 1:
            start = Literal(IntegerLyraType(), "0")
            stops = self.semantics(stmt.arguments[0], state, interpreter).result
            step = Literal(IntegerLyraType(), "1")
            for stop in stops:
                result.add(Range(stmt.typ, start, stop, step))
            state.result = result
            return state
        elif len(stmt.arguments) == 2:
            starts = self.semantics(stmt.arguments[0], state, interpreter).result
            stops = self.semantics(stmt.arguments[1], state, interpreter).result
            step = Literal(IntegerLyraType(), "1")
            for start in starts:
                for stop in stops:
                    result.add(Range(stmt.typ, start, stop, step))
            state.result = result
            return state
        elif len(stmt.arguments) == 3:
            starts = self.semantics(stmt.arguments[0], state, interpreter).result
            stops = self.semantics(stmt.arguments[1], state, interpreter).result
            steps = self.semantics(stmt.arguments[2], state, interpreter).result
            for start in starts:
                for stop in stops:
                    for step in steps:
                        result.add(Range(stmt.typ, start, stop, step))
            state.result = result
            return state
        error = f"Call to {stmt.name} with unexpected number of arguments!"
        raise ValueError(error)

    def count_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to 'count'.

        :param stmt: call to 'count' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for arg in argument:
            result.add(VariableIdentifier(stmt.typ, arg.name))
        state.result = result
        return state

    def find_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to 'find'.

        :param stmt: call to 'find' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for arg in argument:
            result.add(VariableIdentifier(stmt.typ, arg.name))
        state.result = result
        return state

    def get_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to 'get'.

        :param stmt: call to 'get' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for arg in argument:
            result.add(VariableIdentifier(arg.typ.val_typ, arg.name))
        state.result = result
        return state

    # TODO: this is a bitvector operation, can it be analyzed more precisely (e.g., like a binary operation)?
    def bitxor_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to '^' (bitwise xor).

        :param stmt: call to '^' (bitwise xor) to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        for arg in argument:
            result.add(VariableIdentifier(stmt.typ, arg.name))
        state.result = result
        return state

    def items_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to 'items'.

        :param stmt: call to 'items' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if isinstance(stmt.arguments[0], VariableAccess):  # target
            state.result = {Items(stmt.typ, stmt.arguments[0].variable)}
        else:
            error = f"Semantics for items() call on non-variable {stmt.arguments[0]} is not yet " \
                    f"implemented!"
            raise NotImplementedError(error)
        return state

    def keys_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to 'keys'.

        :param stmt: call to 'keys' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if isinstance(stmt.arguments[0], VariableAccess):  # target
            state.result = {Keys(stmt.typ, stmt.arguments[0].variable)}
        else:
            error = f"Semantics for keys() call on non-variable {stmt.arguments[0]} is not yet " \
                    f"implemented!"
            raise NotImplementedError(error)
        return state

    def values_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to 'values'.

        :param stmt: call to 'values' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if isinstance(stmt.arguments[0], VariableAccess):     # target
            state.result = {Values(stmt.typ, stmt.arguments[0].variable)}
        else:
            error = f"Semantics for values() call on non-variable {stmt.arguments[0]} is not yet "\
                    f"implemented!"
            raise NotImplementedError(error)
        return state

    def lower_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of calls to 'lower'.

        :param stmt: call to 'lower' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        # treat as just the target expression (forget about call)
        return self.semantics(stmt.arguments[0], state, interpreter)     # target

    def raise_semantics(self, _, state: State, interpreter: Interpreter) -> State:
        """Semantics of raising an Error.

        :param _: raise statement to be executed
        :param state: state before executing the raise Error
        :return: state modified by the raise
        """
        return state.raise_error()

    def _unary_operation(self, stmt: Call, operator: UnaryOperation.Operator, state, interpreter):
        """Semantics of a call to a unary operation.

        :param stmt: call to unary operation to be executed
        :param operator: unary operator
        :param state: state before executing the call statements
        :return: state modified by the call statement
        """
        assert len(stmt.arguments) == 1  # unary operations have exactly one argument
        argument = self.semantics(stmt.arguments[0], state, interpreter).result
        result = set()
        if isinstance(operator, UnaryArithmeticOperation.Operator):
            for expression in argument:
                operation = UnaryArithmeticOperation(stmt.typ, operator, expression)
                result.add(operation)
        elif isinstance(operator, UnaryBooleanOperation.Operator):
            for expression in argument:
                operation = UnaryBooleanOperation(stmt.typ, operator, expression)
                result.add(operation)
        else:
            error = f"Semantics for unary operation {operator} is not yet implemented!"
            raise NotImplementedError(error)
        state.result = result
        return state

    def not_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '!' (negation).

        :param stmt: call to '!' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._unary_operation(stmt, UnaryBooleanOperation.Operator.Neg, state, interpreter)

    def uadd_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '+' (unary plus).

        :param stmt: call to '+' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = UnaryArithmeticOperation.Operator.Add
        return self._unary_operation(stmt, operator, state, interpreter)

    def usub_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '-' (unary minus).

        :param stmt: call to '-' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = UnaryArithmeticOperation.Operator.Sub
        return self._unary_operation(stmt, operator, state, interpreter)

    def _binary_operation(self, stmt: Call, operator: BinaryOperation.Operator, state, interpreter):
        """Semantics of a call to a binary operation.

        :param stmt: call to binary operation to be executed
        :param operator: binary operator
        :param state: state before executing the call statements
        :return: state modified by the call statement
        """
        arguments = list()
        updated = state
        for i in range(len(stmt.arguments)):
            updated = self.semantics(stmt.arguments[i], updated, interpreter)
            arguments.append(updated.result)
        assert len(arguments) >= 2      # binary operations have at least two arguments
        result = set()
        if isinstance(operator, BinaryArithmeticOperation.Operator):
            for product in itertools.product(*arguments):
                operation = product[0]
                for i in range(1, len(arguments)):
                    right = product[i]
                    operation = BinaryArithmeticOperation(stmt.typ, operation, operator, right)
                result.add(operation)
        elif isinstance(operator, BinarySequenceOperation.Operator):
            for product in itertools.product(*arguments):
                operation = product[0]
                for i in range(1, len(arguments)):
                    right = product[i]
                    operation = BinarySequenceOperation(stmt.typ, operation, operator, right)
                result.add(operation)
        elif isinstance(operator, BinaryComparisonOperation.Operator):
            for product in itertools.product(*arguments):
                operation = product[0]
                for i in range(1, len(arguments)):
                    right = product[i]
                    operation = BinaryComparisonOperation(stmt.typ, operation, operator, right, forloop=stmt.forloop)
                result.add(operation)
        elif isinstance(operator, BinaryBooleanOperation.Operator):
            for product in itertools.product(*arguments):
                operation = product[0]
                for i in range(1, len(arguments)):
                    right = product[i]
                    operation = BinaryBooleanOperation(stmt.typ, operation, operator, right)
                result.add(operation)
        else:
            error = f"Semantics for binary operator {operator} is not yet implemented!"
            raise NotImplementedError(error)
        state.result = result
        return state

    def add_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '+' (addition or concatenation).

        :param stmt: call to '+' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if isinstance(stmt.typ, (StringLyraType, ListLyraType, TupleLyraType)):
            operator = BinarySequenceOperation.Operator.Concat
            return self._binary_operation(stmt, operator, state, interpreter)
        operator = BinaryArithmeticOperation.Operator.Add
        return self._binary_operation(stmt, operator, state, interpreter)

    def sub_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '-' (subtraction).

        :param stmt: call to '-' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryArithmeticOperation.Operator.Sub
        return self._binary_operation(stmt, operator, state, interpreter)

    def mult_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '*' (multiplication, not repetition).

        :param stmt: call to '*' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryArithmeticOperation.Operator.Mult
        return self._binary_operation(stmt, operator, state, interpreter)

    def div_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '/' (division).

        :param stmt: call to '/' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryArithmeticOperation.Operator.Div
        return self._binary_operation(stmt, operator, state, interpreter)

    def mod_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '%' (modulo).

        :param stmt: call to '%' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryArithmeticOperation.Operator.Mod
        return self._binary_operation(stmt, operator, state, interpreter)

    def eq_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '==' (equality).

        :param stmt: call to '==' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.Eq
        return self._binary_operation(stmt, operator, state, interpreter)

    def noteq_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '!=' (inequality).

        :param stmt: call to '!=' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.NotEq
        return self._binary_operation(stmt, operator, state, interpreter)

    def lt_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '<' (less than).

        :param stmt: call to '<' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.Lt
        return self._binary_operation(stmt, operator, state, interpreter)

    def lte_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '<=' (less than or equal to).

        :param stmt: call to '<=' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.LtE
        return self._binary_operation(stmt, operator, state, interpreter)

    def gt_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '>' (greater than).

        :param stmt: call to '>' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.Gt
        return self._binary_operation(stmt, operator, state, interpreter)

    def gte_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to '>=' (greater than or equal to).

        :param stmt: call to '>=' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.GtE
        return self._binary_operation(stmt, operator, state, interpreter)

    def is_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'is' (identity).

        :param stmt: call to 'is' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.Is
        return self._binary_operation(stmt, operator, state, interpreter)

    def isnot_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'is not' (mismatch).

        :param stmt: call to 'is not' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.IsNot
        return self._binary_operation(stmt, operator, state, interpreter)

    def in_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'in' (membership).

        :param stmt: call to 'in' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.In
        return self._binary_operation(stmt, operator, state, interpreter)

    def notin_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'not in' (non-membership).

        :param stmt: call to 'not in' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryComparisonOperation.Operator.NotIn
        return self._binary_operation(stmt, operator, state, interpreter)

    def and_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'and'.

        :param stmt: call to 'add' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryBooleanOperation.Operator.And
        return self._binary_operation(stmt, operator, state, interpreter)

    def or_call_semantics(self, stmt: Call, state: State, interpreter: Interpreter) -> State:
        """Semantics of a call to 'or'.

        :param stmt: call to 'or' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        operator = BinaryBooleanOperation.Operator.Or
        return self._binary_operation(stmt, operator, state, interpreter)


class DefaultSemantics(ExpressionSemantics, BuiltInCallSemantics):
    """Default semantics of statements.

    The semantics is independent of the direction (forward/backward) of the analysis."""
    pass
