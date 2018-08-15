"""
Semantics
=========

Lyra's internal semantics of statements.

:Authors: Caterina Urban and Simon Wehrli
"""


import itertools
import re

from lyra.abstract_domains.state import State
from lyra.core.expressions import BinaryArithmeticOperation, Subscription, Slicing, \
    LengthIdentifier, VariableIdentifier, Range, Expression, BinarySequenceOperation
from lyra.core.expressions import BinaryBooleanOperation, Input, TupleDisplay, ListDisplay, \
    Literal, SetDisplay, DictDisplay, Items, Keys, Values
from lyra.core.expressions import BinaryOperation, BinaryComparisonOperation
from lyra.core.expressions import UnaryArithmeticOperation, UnaryBooleanOperation
from lyra.core.expressions import UnaryOperation
from lyra.core.statements import Statement, VariableAccess, LiteralEvaluation, Call, \
    TupleDisplayAccess, ListDisplayAccess, SetDisplayAccess, DictDisplayAccess, \
    SubscriptionAccess, SlicingAccess
from lyra.core.types import LyraType, BooleanLyraType, IntegerLyraType, FloatLyraType, \
    StringLyraType, TupleLyraType, ListLyraType

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

    def semantics(self, stmt: Statement, state: State) -> State:
        """Semantics of a statement.

        :param stmt: statement to be executed
        :param state: state before executing the statement
        :return: state modified by the statement execution
        """
        name = '{}_semantics'.format(camel_to_snake(stmt.__class__.__name__))
        if hasattr(self, name):
            return getattr(self, name)(stmt, state)
        error = f"Semantics for statement {stmt} of type {type(stmt)} not yet implemented! "
        raise NotImplementedError(error + f"You must provide method {name}(...)")


class ExpressionSemantics(Semantics):
    """Semantics of expression evaluations and accesses."""

    # noinspection PyMethodMayBeStatic
    def literal_evaluation_semantics(self, stmt: LiteralEvaluation, state: State) -> State:
        """Semantics of a literal evaluation.

        :param stmt: literal evaluation statement to be executed
        :param state: state before executing the literal evaluation
        :return: stated modified by the literal evaluation
        """
        state.result = {stmt.literal}
        return state

    # noinspection PyMethodMayBeStatic
    def variable_access_semantics(self, stmt: VariableAccess, state: State) -> State:
        """Semantics of a variable access.

        :param stmt: variable access statement to be executed
        :param state: state before executing the variable access
        :return: state modified by the variable access
        """
        state.result = {stmt.variable}
        return state

    def list_display_access_semantics(self, stmt: ListDisplayAccess, state: State) -> State:
        """Semantics of a list display access.

        :param stmt: list display access statement to be executed
        :param state: state before executing the list display access
        :return: state modified by the list display access
        """
        items = [self.semantics(item, state).result for item in stmt.items]
        result = set()
        for combination in itertools.product(*items):
            display = ListDisplay(stmt.typ, list(combination))
            result.add(display)
        state.result = result
        return state

    def tuple_display_access_semantics(self, stmt: TupleDisplayAccess, state: State) -> State:
        """Semantics of a tuple display access.

                :param stmt: tuple display access statement to be executed
                :param state: state before executing the tuple display access
                :return: state modified by the tuple display access
                """
        items = [self.semantics(item, state).result for item in stmt.items]
        result = set()
        for combination in itertools.product(*items):
            display = TupleDisplay(stmt.typ, list(combination))
            result.add(display)
        state.result = result
        return state

    def set_display_access_semantics(self, stmt: SetDisplayAccess, state: State) -> State:
        """Semantics of a set display access.

        :param stmt: set display access statement to be executed
        :param state: state before executing the set display access
        :return: state modified by the set display access
        """
        items = [self.semantics(item, state).result for item in stmt.items]
        result = set()
        for combination in itertools.product(*items):
            display = SetDisplay(stmt.typ, list(combination))
            result.add(display)
        state.result = result
        return state

    def dict_display_access_semantics(self, stmt: DictDisplayAccess, state: State) -> State:
        """Semantics of a list display access.

        :param stmt: dictionary display access statement to be executed
        :param state: state before executing the dictionary display access
        :return: state modified by the dictionary display access
        """
        keys = [self.semantics(k, state).result for k in stmt.keys]  # List[Set[Expression]]
        values = [self.semantics(v, state).result for v in stmt.values]
        result = set()
        if keys:  # not empty
            for combination in itertools.product(*map(itertools.product, keys, values)):
                unzip = list(zip(*combination))  # to create two separate lists for keys and values
                display = DictDisplay(stmt.typ, list(unzip[0]), list(unzip[1]))
                result.add(display)
        else:
            result.add(DictDisplay(stmt.typ, list(), list()))
        state.result = result
        return state

    def subscription_access_semantics(self, stmt: SubscriptionAccess, state: State) -> State:
        """Semantics of a subscription access.

        :param stmt: subscription access statement to be executed
        :param state: state before executing the subscription access
        :return: state modified by the subscription access
        """
        target = self.semantics(stmt.target, state).result
        key = self.semantics(stmt.key, state).result
        result = set()
        for primary, index in itertools.product(target, key):
            subscription = Subscription(primary.typ, primary, index)
            result.add(subscription)
        state.result = result
        return state

    def slicing_access_semantics(self, stmt: SlicingAccess, state: State) -> State:
        """Semantics of a slicing access.

        :param stmt: slicing access statement to be executed
        :param state: state before executing the slicing access
        :return: state modified by the slicing access
        """
        target = self.semantics(stmt.target, state).result
        lower = self.semantics(stmt.lower, state).result
        upper = self.semantics(stmt.upper, state).result if stmt.upper else {None}
        stride = self.semantics(stmt.stride, state).result if stmt.stride else {None}
        result = set()
        for primary, start, stop, step in itertools.product(target, lower, upper, stride):
            slicing = Slicing(primary.typ, primary, start, stop, step)
            result.add(slicing)
        state.result = result
        return state


class CallSemantics(Semantics):
    """Semantics of function/method calls."""

    def call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a function/method call.

        :param stmt: call statement to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        name = '{}_call_semantics'.format(stmt.name)
        if hasattr(self, name):
            return getattr(self, name)(stmt, state)
        return getattr(self, 'user_defined_call_semantics')(stmt, state)


class BuiltInCallSemantics(CallSemantics):
    """Semantics of built-in function/method calls."""

    def _cast_call_semantics(self, stmt: Call, state: State, typ: LyraType) -> State:
        """Semantics of a call to 'int' or 'bool'.

        :param stmt: call to 'int' or 'bool' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if len(stmt.arguments) != 1:
            error = f"Semantics for multiple arguments of {stmt.name} is not yet implemented!"
            raise NotImplementedError(error)
        argument = self.semantics(stmt.arguments[0], state).result
        result = set()
        for expression in argument:
            if isinstance(expression, Input):
                result.add(Input(typ))
            elif isinstance(expression, Literal):
                result.add(Literal(typ, expression.val))
            elif isinstance(expression, VariableIdentifier):
                result.add(VariableIdentifier(typ, expression.name))
            elif isinstance(expression, Subscription):
                result.add(Subscription(typ, expression.target, expression.key))
            else:
                error = f"Argument of type {expression.typ} of {stmt.name} is not yet supported!"
                raise NotImplementedError(error)
        state.result = result
        return state

    def bool_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'bool'.

        :param stmt: call to 'bool' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._cast_call_semantics(stmt, state, BooleanLyraType())

    def int_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'int'.

        :param stmt: call to 'int' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._cast_call_semantics(stmt, state, IntegerLyraType())

    def float_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'float'.

        :param stmt: call to 'float' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._cast_call_semantics(stmt, state, FloatLyraType())

    def list_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'list'.

        :param stmt: call to 'list' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            state.result = {ListDisplay(stmt.typ, list())}
            return state
        raise NotImplementedError(f"Semantics for {stmt} is not yet implemented!")

    def set_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'set'.

        :param stmt: call to 'set' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            state.result = {SetDisplay(stmt.typ, list())}
            return state
        raise NotImplementedError(f"Semantics for {stmt} is not yet implemented!")

    def dict_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'dict'.

        :param stmt: call to 'dict' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if not stmt.arguments:
            state.result = {SetDisplay(stmt.typ, list())}
            return state
        raise NotImplementedError(f"Semantics for {stmt} is not yet implemented!")

    def len_call_semantics(self, stmt: Call, state: State) -> State:
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
        error = f"Semantics for length of {argument} is not yet implemented!"
        raise NotImplementedError(error)

    def split_call_semantics(self, stmt: Call, state: State) -> State:
        if len(stmt.arguments) != 1:
            error = f"Semantics for multiple arguments of {stmt.name} is not yet implemented!"
            raise NotImplementedError(error)
        argument = self.semantics(stmt.arguments[0], state).result
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
            elif isinstance(arg, VariableIdentifier):   # x.split()
                result.add(VariableIdentifier(typ, arg.name))
                continue
            elif isinstance(arg, Input):                # input().split()
                result.add(Input(typ))
                continue
            error = f"Call to {stmt.name} of unexpected argument!"
            raise ValueError(error)
        state.result = result
        return state

    # noinspection PyMethodMayBeStatic
    def input_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a calls to 'input'.

        :param stmt: call to 'input' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        state.result = {Input(stmt.typ)}
        return state

    def print_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'print'.

        :param stmt: call to 'print' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if len(stmt.arguments) != 1:
            error = f"Semantics for multiple arguments of {stmt.name} is not yet implemented!"
            raise NotImplementedError(error)
        argument = self.semantics(stmt.arguments[0], state).result
        return state.output(argument)

    def range_call_semantics(self, stmt: Call, state: State) -> State:
        result = set()
        if len(stmt.arguments) == 1:
            start = Literal(IntegerLyraType(), "0")
            stops = self.semantics(stmt.arguments[0], state).result
            step = Literal(IntegerLyraType(), "1")
            for stop in stops:
                result.add(Range(stmt.typ, start, stop, step))
            state.result = result
            return state
        elif len(stmt.arguments) == 2:
            starts = self.semantics(stmt.arguments[0], state).result
            stops = self.semantics(stmt.arguments[1], state).result
            step = Literal(IntegerLyraType(), "1")
            for start in starts:
                for stop in stops:
                    result.add(Range(stmt.typ, start, stop, step))
            state.result = result
            return state
        elif len(stmt.arguments) == 3:
            starts = self.semantics(stmt.arguments[0], state).result
            stops = self.semantics(stmt.arguments[1], state).result
            steps = self.semantics(stmt.arguments[2], state).result
            for start in starts:
                for stop in stops:
                    for step in steps:
                        result.add(Range(stmt.typ, start, stop, step))
            state.result = result
            return state
        error = f"Call to {stmt.name} with unexpected number of arguments!"
        raise ValueError(error)

    def items_call_semantics(self, stmt: Call, state: State) -> State:
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

    def keys_call_semantics(self, stmt: Call, state: State) -> State:
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

    def values_call_semantics(self, stmt: Call, state: State) -> State:
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

    # TODO: define default call semantics instead for usage?
    def lower_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of calls to 'lower'.

        :param stmt: call to 'lower' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        # treat as just the target expression (forget about call)
        return self.semantics(stmt.arguments[0], state)     # target

    def raise_semantics(self, _, state: State) -> State:
        """Semantics of raising an Error.

        :param _: raise statement to be executed
        :param state: state before executing the raise Error
        :return: state modified by the raise
        """
        return state.raise_error()

    def _unary_operation(self, stmt: Call, operator: UnaryOperation.Operator, state: State):
        """Semantics of a call to a unary operation.

        :param stmt: call to unary operation to be executed
        :param operator: unary operator
        :param state: state before executing the call statements
        :return: state modified by the call statement
        """
        assert len(stmt.arguments) == 1  # unary operations have exactly one argument
        argument = self.semantics(stmt.arguments[0], state).result
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

    def not_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '!' (negation).

        :param stmt: call to '!' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._unary_operation(stmt, UnaryBooleanOperation.Operator.Neg, state)

    def uadd_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '+' (unary plus).

        :param stmt: call to '+' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._unary_operation(stmt, UnaryArithmeticOperation.Operator.Add, state)

    def usub_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '-' (unary minus).

        :param stmt: call to '-' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._unary_operation(stmt, UnaryArithmeticOperation.Operator.Sub, state)

    def _binary_operation(self, stmt: Call, operator: BinaryOperation.Operator, state: State):
        """Semantics of a call to a binary operation.

        :param stmt: call to binary operation to be executed
        :param operator: binary operator
        :param state: state before executing the call statements
        :return: state modified by the call statement
        """
        arguments = list()
        updated = state
        for i in range(len(stmt.arguments)):
            updated = self.semantics(stmt.arguments[i], updated)
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
                    operation = BinaryComparisonOperation(stmt.typ, operation, operator, right)
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

    def add_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '+' (addition or concatenation).

        :param stmt: call to '+' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        if isinstance(stmt.typ, (StringLyraType, ListLyraType, TupleLyraType)):
            return self._binary_operation(stmt, BinarySequenceOperation.Operator.Concat, state)
        return self._binary_operation(stmt, BinaryArithmeticOperation.Operator.Add, state)

    def sub_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '-' (subtraction).

        :param stmt: call to '-' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryArithmeticOperation.Operator.Sub, state)

    def mult_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '*' (multiplication, not repetition).

        :param stmt: call to '*' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryArithmeticOperation.Operator.Mult, state)

    def div_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '/' (division).

        :param stmt: call to '/' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryArithmeticOperation.Operator.Div, state)

    def eq_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '==' (equality).

        :param stmt: call to '==' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.Eq, state)

    def noteq_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '!=' (inequality).

        :param stmt: call to '!=' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.NotEq, state)

    def lt_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '<' (less than).

        :param stmt: call to '<' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.Lt, state)

    def lte_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '<=' (less than or equal to).

        :param stmt: call to '<=' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.LtE, state)

    def gt_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '>' (greater than).

        :param stmt: call to '>' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.Gt, state)

    def gte_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to '>=' (greater than or equal to).

        :param stmt: call to '>=' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement"""
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.GtE, state)

    def is_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'is' (identity).

        :param stmt: call to 'is' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.Is, state)

    def isnot_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'is not' (mismatch).

        :param stmt: call to 'is not' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.IsNot, state)

    def in_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'in' (membership).

        :param stmt: call to 'in' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.In, state)

    def notin_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'not in' (non-membership).

        :param stmt: call to 'not in' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryComparisonOperation.Operator.NotIn, state)

    def and_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'and'.

        :param stmt: call to 'add' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryBooleanOperation.Operator.And, state)

    def or_call_semantics(self, stmt: Call, state: State) -> State:
        """Semantics of a call to 'or'.

        :param stmt: call to 'or' to be executed
        :param state: state before executing the call statement
        :return: state modified by the call statement
        """
        return self._binary_operation(stmt, BinaryBooleanOperation.Operator.Or, state)


class DefaultSemantics(ExpressionSemantics, BuiltInCallSemantics):
    """Default semantics of statements.

    The semantics is independent of the direction (forward/backward) of the analysis."""
    pass
