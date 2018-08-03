"""
Assumption Abstract Domains
===========================

Abstract domains to be used for **input data assumption analysis**.

:Authors: Caterina Urban and Radwa Sherif Abdelbar
"""
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from copy import deepcopy
from enum import Enum
from typing import List, Dict, Type, Any, Union, Tuple, Set, Optional, Generator
from lyra.abstract_domains.lattice import Lattice, BottomMixin
from lyra.abstract_domains.stack import Stack
from lyra.abstract_domains.state import State
from lyra.assumption.error import CheckerError
from lyra.assumption.error import CheckerError
from lyra.core.expressions import VariableIdentifier, Expression, BinaryComparisonOperation, \
    Range, Literal, NegationFreeNormalExpression, UnaryBooleanOperation, BinaryBooleanOperation, \
    ExpressionVisitor, Input, ListDisplay, AttributeReference, Subscription, Slicing, \
    UnaryArithmeticOperation, BinaryArithmeticOperation, LengthIdentifier, Identifier
from lyra.core.statements import ProgramPoint
from lyra.core.types import IntegerLyraType, FloatLyraType, StringLyraType, BooleanLyraType, \
    ListLyraType
from lyra.core.utils import copy_docstring

class JSONMixin(Lattice, metaclass=ABCMeta):
    """Mixin to add a mechanism for converting a lattice to and from JSON format."""

    @abstractmethod
    def to_json(self) -> dict:
        """Convert the current lattice element to JSON format.

        :return: JSON format of the current lattice element
        """

    @staticmethod
    @abstractmethod
    def from_json(json: dict) -> 'JSONMixin':
        """Reconstruct a lattice element from its JSON format.

        :param json: JSON format of a lattice element
        :return: reconstructed lattice element from its JSON format
        """

    @abstractmethod
    def check_input(self, *args):
        """
        Checks if the given input value satisfies the constraints of the current lattice element.
        :return:
        """

class InputMixin(State, metaclass=ABCMeta):
    """Mixin to add a mechanism for recording and retrieving constraints on the input data.

    Constraints are recorded in the class member ``inputs``, which is a map
    from each program point to the list of constraints on the input data read at that point.
    """
    inputs: Dict[ProgramPoint, List[JSONMixin]]

    def __init__(self, precursory: State = None):
        super().__init__(precursory)
        type(self).inputs = defaultdict(list)

    @abstractmethod
    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'InputMixin':
        """Replace a variable with an expression.

        .. note::
            The new variables appearing in the replacing expression are added to the current state.

        :param variable: variable to be replaced
        :param expression: expression replacing the variable
        :return: current state modified to manifest the replacement
        """

    @abstractmethod
    def unify(self, other: 'InputMixin') -> 'InputMixin':
        """Unification of the environment of the current state
        with the environment of another state.

        This is needed when new variables are introduced by ``replace()``
        to represent input expressions. The unification should match variables
        in the order of the program points on which they depend.

        :param other: state whose environment we want to unify with
        :return: current state modified to reflect the unification
        """

    @copy_docstring(State.less_equal)
    def less_equal(self, other: 'InputMixin'):
        self.unify(other)
        return super().less_equal(other.unify(self))

    @copy_docstring(State.join)
    def join(self, other: 'InputMixin'):
        self.unify(other)
        return super().join(other.unify(self))

    @copy_docstring(State.join)
    def meet(self, other: 'InputMixin'):
        self.unify(other)
        return super().meet(other.unify(self))

    @copy_docstring(State.join)
    def widening(self, other: 'InputMixin'):
        self.unify(other)
        return super().widening(other.unify(self))

    def record(self, constraint: JSONMixin) -> 'InputMixin':
        """Record an constraint.

        :param constraint: constraint to be recorded
        :return: current state modified to record the constraint
        """
        type(self).inputs[self.pp].append(constraint)
        return self

    def retrieve(self) -> List[JSONMixin]:
        """Retrieve and forget the constraints corresponding to the current program point.

        .. warning::
            The current state is modified to forget the returned constraints.

        :return: the list of constraints corresponding to the current program point
        """
        return type(self).inputs.pop(self.pp, list())


class MultiplierEvaluator(ExpressionVisitor):

    def visit_Literal(self, expr: 'Literal', pp_value=None, lines_involved=None):
        if expr.typ == IntegerLyraType():
            return int(expr.val)
        if expr.typ == FloatLyraType():
            return float(expr.val)

        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_Input(self, expr: 'Input', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_VariableIdentifier(self, expr: 'VariableIdentifier', pp_value=None, lines_involved=None):
        if expr in pp_value:
            (line_number, input_value) = pp_value[expr]
            if input_value is None:
                lines_involved.append(line_number)
            return input_value

    def visit_LengthIdentifier(self, expr: 'LengthIdentifier', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_ListDisplay(self, expr: 'ListDisplay', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_Range(self, expr: 'Range', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_AttributeReference(self, expr: 'AttributeReference', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_Subscription(self, expr: 'Subscription', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_Slicing(self, expr: 'Slicing', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation', pp_value=None, lines_involved=None):
        eval = self.visit(expr.expression, pp_value)
        if eval is None or expr.operator == UnaryArithmeticOperation.Operator.Add:
            return eval
        if expr.operator == UnaryArithmeticOperation.Operator.Sub:
            return -eval
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation', pp_value=None, lines_involved=None):
        left = self.visit(expr.left, pp_value)
        right = self.visit(expr.right, pp_value)
        if left is None or right is None:
            return None
        op = expr.operator
        if op == BinaryArithmeticOperation.Operator.Sub:
            return left - right
        if op == BinaryArithmeticOperation.Operator.Add:
            return left + right
        if op == BinaryArithmeticOperation.Operator.Mult:
            return left * right
        if op == BinaryArithmeticOperation.Operator.Div:
            return left / right

    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))

    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', pp_value=None, lines_involved=None):
        raise NotImplementedError("Multiplier evaluator not define for type {}".format(expr.typ))


class AssumptionState(State):
    """Assumption analysis state. An element of the assumption abstract domain.

    Reduced product of a list of constraining states,
    which collect constraints on the program variables and (indirectly) on the input data,
    and a stack of assumptions on the input data,
    which (directly) constraints the input data read from the current program point.

    .. document private methods
    .. automethod:: AssumptionState._assume
    .. automethod:: AssumptionState._substitute
    """
    class InputStack(Stack, State):
        """Stack of assumptions on the input data.

        .. document private methods
        .. automethod:: InputStack._assume
        .. automethod:: InputStack._substitute
        """
        class InputLattice(BottomMixin):
            """Assumptions on the input data.

            Each assumption is a (possibly symbolic) repetition of constraints on the input data.
            A constraint can be:
            * a basic constraint, i.e., a tuple of lattices (l, ...)
              which indicates that an input data point is expected and restricts its possible value
            * a star constraint, i.e., ★
              which indicates that any number of input data points is expected
            * another symbolically repeated assumption

            Let S be the set of all possible sequences of input data points.
            The concretization function Ɣ: InputLattice -> 𝒫(S) is defined as follows::

                Ɣ(1 * [★]) = S
                ...
                Ɣ(1 * [(l1, l2), ★]) = { xs ∈ S | x ∈ Ɣ(l1) ⋂ Ɣ(l2) }
                ...
                Ɣ(n * [(l1, l2)]) = { x^n ∈ S | x ∈ Ɣ(l1) ⋂ Ɣ(l2) }
                ...
                Ɣ(1 * [(l1, l2)]) = { x ∈ S | x ∈ Ɣ(l1) ⋂ Ɣ(l2) }
                ...
                Ɣ(1 * []) = { ε }

            .. document private methods
            .. automethod:: InputLattice._less_equal
            .. automethod:: InputLattice._meet
            .. automethod:: InputLattice._join
            .. automethod:: InputLattice._widening
            """
            InputLattice = 'AssumptionState.InputStack.InputLattice'
            StarConstraint = Tuple[ProgramPoint, ...]
            BasicConstraint = Tuple[ProgramPoint, Tuple[JSONMixin, ...]]
            InputConstraint = Union[StarConstraint, BasicConstraint, InputLattice]

            def __init__(self, multiplier: Expression = Literal(IntegerLyraType(), "1"),
                         constraints: List[InputConstraint] = list()):
                super().__init__()
                self._multiplier = multiplier
                self._constraints = constraints

            @property
            def multiplier(self):
                """Current multiplier."""
                return self._multiplier

            @property
            def constraints(self):
                """Current list of constraints."""
                return self._constraints

            def __repr__(self):
                def do(constraint):
                    if isinstance(constraint, tuple):
                        # the constraint is a StarConstraint or a BasicConstraint
                        if not constraint:  # the constraint is a StarConstraint
                            return "★"
                        else:  # the constraint is a BasicConstraint
                            return "{}:{}".format(constraint[0].line, constraint[1])
                    else:  # the constraint is an InputLattice
                        return "{}".format(constraint) if constraint.constraints else ""
                multiplier = self.multiplier
                is_one = isinstance(multiplier, Literal) and multiplier.val == "1"
                repetitions = "" if is_one else "{} * ".format(multiplier)
                single = len(self.constraints) == 1
                formatted = (do(constraint) for constraint in self.constraints)
                constraints = ", ".join(constraint for constraint in formatted if constraint)
                beginning = "" if is_one or (single and constraints) else "["
                ending = "" if is_one or (single and constraints) else "]"
                assumption = repetitions + beginning + constraints + ending
                return assumption if assumption else "ε"

            @copy_docstring(BottomMixin.top)
            def top(self):
                """The top lattice element is ``1 * [★]``."""
                one = Literal(IntegerLyraType(), "1")
                return self._replace(AssumptionState.InputStack.InputLattice(one, [()]))

            @copy_docstring(BottomMixin.is_top)
            def is_top(self) -> bool:
                def is_star(constraint):
                    return isinstance(constraint, tuple) and not constraint
                multiplier = self.multiplier
                one = isinstance(multiplier, Literal) and multiplier.val == "1"
                single = len(self.constraints) == 1
                return one and single and is_star(self.constraints[0])

            @copy_docstring(BottomMixin._less_equal)
            def _less_equal(self, other: InputLattice) -> bool:
                def do(constraint1, constraint2) -> bool:
                    if isinstance(constraint1, tuple) and isinstance(constraint2, tuple):
                        # the constraints are StarConstraints or BasicConstraints
                        if not constraint1 and not constraint2:
                            # the constraints are StarConstraints
                            return True
                        else:  # the constraints are BasicConstraints
                            l1: Tuple[JSONMixin, ...] = constraint1[1]
                            l2: Tuple[JSONMixin, ...] = constraint2[1]
                            return all(x.less_equal(y) for x, y in zip(l1, l2))
                    else:   # the constraints are InputLattices
                        m: bool = constraint1.multiplier == constraint2.multiplier
                        c1 = constraint1.constraints
                        c2 = constraint2.constraints
                        c: bool = len(c2) == len(c1) and all(do(x, y) for x, y in zip(c1, c2))
                        return m and c
                multiplier1 = self.multiplier
                multiplier2 = other.multiplier
                assert isinstance(multiplier1, Literal) and multiplier1.val == "1"
                assert isinstance(multiplier2, Literal) and multiplier2.val == "1"
                if len(self.constraints) == len(other.constraints):
                    return all(do(x, y) for x, y in zip(self.constraints, other.constraints))
                return False

            @copy_docstring(BottomMixin._join)
            def _join(self, other: InputLattice) -> InputLattice:
                def do(constraint1, constraint2):
                    if isinstance(constraint1, tuple) and isinstance(constraint2, tuple):
                        # the constraints are StarConstraints or BasicConstraints
                        if not constraint1 and not constraint2:
                            # the constraints are StarConstraints
                            return ()
                        else:   # the constraints are BasicConstraints
                            pp1: ProgramPoint = constraint1[0]
                            pp2: ProgramPoint = constraint2[0]
                            pp: ProgramPoint = pp1 if pp1.line <= pp2.line else pp2
                            l1: Tuple[JSONMixin, ...] = constraint1[1]
                            l2: Tuple[JSONMixin, ...] = constraint2[1]
                            return pp, tuple(x.join(y) for x, y in zip(l1, l2))
                    else:   # the constraints are InputLattices
                        assert isinstance(constraint1, AssumptionState.InputStack.InputLattice)
                        assert isinstance(constraint2, AssumptionState.InputStack.InputLattice)
                        m1: Expression = constraint1.multiplier
                        m2: Expression = constraint2.multiplier
                        c1 = constraint1.constraints
                        c2 = constraint2.constraints
                        is_one1 = isinstance(m1, Literal) and m1.val == "1"
                        is_one2 = isinstance(m2, Literal) and m2.val == "1"
                        if is_one1 and is_one2:
                            m = Literal(IntegerLyraType(), "1")
                            c = [do(x, y) for x, y in zip(c1, c2)]
                            if len(c1) != len(c2):  # lengths of list of constraints are different
                                c.append(())  # add a star constraint
                        else:
                            assert m1 == m2
                            m: Expression = m1
                            c = [do(x, y) for x, y in zip(c1, c2)]
                            c.extend(c1[len(c2):])
                            c.extend(c2[len(c1):])
                        return AssumptionState.InputStack.InputLattice(m, c)
                multiplier1 = self.multiplier
                multiplier2 = other.multiplier
                assert isinstance(multiplier1, Literal) and multiplier1.val == "1"
                assert isinstance(multiplier2, Literal) and multiplier2.val == "1"
                constraints = [do(x, y) for x, y in zip(self.constraints, other.constraints)]
                one = Literal(IntegerLyraType(), "1")
                return self._replace(AssumptionState.InputStack.InputLattice(one, constraints))

            @copy_docstring(BottomMixin._meet)
            def _meet(self, other: InputLattice) -> InputLattice:   # TODO
                return self

            @copy_docstring(BottomMixin._widening)
            def _widening(self, other: InputLattice) -> InputLattice:
                """``self \/ other = self ▽ other``."""
                return self._join(other)

            def repeat(self, multiplier: Expression) -> InputLattice:
                """Repeat the current assumption on the input data.

                :param multiplier: repetitions to be performed
                :return: current lattice element modified to repeat the assumption
                """
                repeated = AssumptionState.InputStack.InputLattice(multiplier, self.constraints)
                return self._replace(repeated)

            def record(self, constraint: InputConstraint) -> InputLattice:
                """Record a constraint on the input data.

                By default, the constraint is added to the current list of recorded constraints.

                When leaving the body of a for loop another time than the first, the constraint
                to be recorded is instead merged with the previously recorded constraint.

                :param constraint: constraint to be recorded
                :return: current lattice element modified to record the constraint
                """
                def do(constraint1, constraint2):
                    if isinstance(constraint1, tuple) and isinstance(constraint2, tuple):
                        # the constraints are BasicConstraints about the same program point
                        assert constraint1 and constraint2 and constraint1[0] == constraint2[0]
                        l1: Tuple[JSONMixin, ...] = constraint1[1]
                        l2: Tuple[JSONMixin, ...] = constraint2[1]
                        return constraint1[0], tuple(x.join(y) for x, y in zip(l1, l2))
                    else:   # the constraints are InputLattices
                        constraints1 = constraint1.constraints
                        constraints2 = constraint2.constraints
                        for i, cs in enumerate(zip(constraints1, constraints2)):
                            if cs[0] != cs[1]:
                                constraint1.constraints[i] = do(cs[0], cs[1])
                        reminder = constraint2.constraints[len(constraint1.constraints):]
                        constraint1.constraints.extend(reminder)
                        return constraint1
                if isinstance(constraint, AssumptionState.InputStack.InputLattice):
                    # the constraint to be recorded is a (possibly empty) repetition
                    m1 = constraint.multiplier
                    if isinstance(m1, Literal) and m1.val == "1" and not constraint.constraints:
                        # the constraint to be recorded is empty
                        return self
                    if self.constraints:
                        # the constraint to be recorded is a non-empty repetition and
                        # there is at least one previously recorded constraint
                        previous = self.constraints[0]
                        if isinstance(previous, AssumptionState.InputStack.InputLattice):
                            # the previously recorded constraint is also a repetition
                            m2 = previous.multiplier
                            if type(m1) == type(m2) and m1 == m2:
                                # we are leaving the body of a for loop another time than the first
                                self.constraints[0] = do(constraint, previous)
                                return self
                self.constraints.insert(0, constraint)
                return self

            def replace(self, variable: VariableIdentifier, expression: Expression):
                """Replace a variable with an expression.

                :param variable: variable to be replaced
                :param expression: expression replacing the variable
                :return: current lattice element modified to manifest the replacement
                """
                def do(constraint):
                    if isinstance(constraint, tuple):
                        # the constraint is a StarConstraint or a BasicConstraint
                        if not constraint:  # the constraint is a StarConstraint
                            return constraint
                        else:   # the constraint is a BasicConstraint
                            lattices = list(constraint[1])
                            for i, lattice in enumerate(lattices):
                                if hasattr(lattice, 'replace'):
                                    lattices[i] = lattice.replace(variable, expression)
                            return constraint[0], tuple(lattices)
                    else:   # the constraint is an InputLattice
                        return constraint.replace(variable, expression)

                multiplier = self.multiplier
                if isinstance(multiplier, VariableIdentifier) and multiplier == variable:
                    multiplier = expression
                constraints = [do(constraint) for constraint in self.constraints]
                replaced = AssumptionState.InputStack.InputLattice(multiplier, constraints)
                return self._replace(replaced)

            _state_names = dict()
            @copy_docstring(JSONMixin.to_json)
            def to_json(self) -> dict:
                def do_multiplier(expression):
                    numerical_types = [IntegerLyraType(), FloatLyraType()]
                    if isinstance(expression, Identifier):
                        return {'type': ['identifier', str(expression.typ)], 'value': expression.name}
                    if isinstance(expression, Literal) and expression.typ in numerical_types:
                        return {'type': ['literal', str(expression.typ)], 'value': expression.val}
                    js = dict()
                    if isinstance(expression, BinaryArithmeticOperation):
                        js['type'] = ['binary_arithmetic', str(expression.typ)]
                        js['left'] = do_multiplier(expression.left)
                        js['operator'] = expression.operator
                        js['right'] = do_multiplier(expression.right)
                        return js
                    raise ValueError("JSON conversion not supported for multiplier {}".format(expression))

                def is_star(constraint): return isinstance(constraint, tuple) and not constraint

                def is_basic(constraint): return isinstance(constraint, tuple) and constraint

                def do_constraint(constraint):
                    if is_star(constraint):
                        return '*'
                    if is_basic(constraint):
                        js = dict()
                        js['pp'] = [constraint[0].line, constraint[0].column]
                        js['lattice_elements'] = []
                        for element in constraint[1]:
                            AssumptionState.InputStack.InputLattice._state_names[type(element).__name__] = type(element)
                            js['lattice_elements'].append({
                                'domain': str(type(element).__name__),
                                'element': element.to_json()
                            })

                        return js
                    if isinstance(constraint, AssumptionState.InputStack.InputLattice):
                        return constraint.to_json()
                js = dict()
                js['multiplier'] = do_multiplier(self.multiplier)
                js['constraints'] = [do_constraint(constraint) for constraint in self.constraints]
                return js

            @staticmethod
            @copy_docstring(JSONMixin.from_json)
            def from_json(json: dict) -> 'JSONMixin':

                def do_type(typ:str):
                    if typ == 'int':
                        return IntegerLyraType()
                    if typ == 'float':
                        return FloatLyraType()
                    if typ == 'string':
                        return StringLyraType()
                    if typ == 'bool':
                        return BooleanLyraType()
                    if typ.startswith("List"):
                        typ = typ[5:-1]
                        return ListLyraType(do_type(typ))

                def do_multiplier(js):
                    types = {'int': IntegerLyraType, 'float': FloatLyraType, 'string': StringLyraType}
                    if js['type'][0] == 'identifier':
                        typ = do_type(js['type'][1])
                        return VariableIdentifier(typ, js['value'])
                    if js['type'][0] == 'literal':
                        typ = do_type(js['type'][1])
                        return Literal(typ, js['value'])
                    if js['type'][0] == 'binary_arithmetic':
                        typ = do_type(js['type'][1])
                        left = do_multiplier(js['left'])
                        operator = js['operator']
                        right = do_multiplier(js['right'])
                        return BinaryArithmeticOperation(typ, left, operator, right)

                def do_constraint(js):
                    if js == '*':
                        return ()
                    if 'pp' in js:  # basic constraint
                        pp = ProgramPoint(js['pp'][0], js['pp'][1])
                        cons = []
                        for element in js['lattice_elements']:
                            state = AssumptionState.InputStack.InputLattice._state_names[element['domain']]
                            cons.append(state.from_json(element['element']))
                        cons = tuple(cons)
                        return pp, cons
                    if 'multiplier' in js:  # input constraint
                        return AssumptionState.InputStack.InputLattice.from_json(js)
                multiplier = do_multiplier(json['multiplier'])
                constraints = [do_constraint(c) for c in json['constraints']]
                return AssumptionState.InputStack.InputLattice(multiplier, constraints)

            @copy_docstring(JSONMixin.check_input)
            def check_input(self, input_generator: Generator, pp_value, line_errors):

                def is_star(constraint): return isinstance(constraint, tuple) and not constraint

                def is_basic(constraint): return isinstance(constraint, tuple) and constraint

                def gen(assumption):
                    if is_star(assumption) or is_basic(assumption):
                        yield assumption
                    else:
                        lines_involved = []
                        m = assumption.multiplier
                        mult = MultiplierEvaluator().visit(m, pp_value, lines_involved)
                        # check for valid multiplier
                        message = ""
                        if mult is None:
                            lines_message = ','.join([str(l) for l in lines_involved])
                            message += "Cannot calculate loop range."
                            message += "Errors on lines: {}.".format(lines_message)
                        elif not isinstance(mult, int):
                            message += "Loop range must be an integer."
                        if len(message) > 0:
                            mult_error = CheckerError(message)
                            raise ValueError(mult_error)
                        for _ in range(mult):
                            for cons in assumption.constraints:
                                yield from gen(cons)

                constraint_generator = gen(self)
                end_of_constraints, end_of_input = False, False
                line_number = 1
                while not end_of_input and not end_of_constraints:
                    try:
                        line_number, input_value = next(input_generator)
                        # print("LINE NUMBER, INPUT VAL", line_number, input_value)
                    except StopIteration:
                        end_of_input = True

                    try:
                        constraint = next(constraint_generator)
                        # print("CONS", constraint)
                    except StopIteration:
                        end_of_constraints = True
                    except ValueError as e:
                        line_errors[line_number].append(e.args[0])
                        break

                    if end_of_constraints or end_of_input:
                        break

                    if is_star(constraint):  # information loss, cannot continue checking
                        error = CheckerError("Not enough information to continue checking after this line.")
                        line_errors[line_number].append(error)
                        end_of_constraints = True



                    if is_basic(constraint):
                        pp = constraint[0]
                        pp = VariableIdentifier(IntegerLyraType(), "{}.{}".format(pp.line, 1))
                        pp_value[pp] = (line_number, input_value)
                        for cons in constraint[1]:
                            cons.check_input(pp, pp_value, line_errors)
                if end_of_input and not end_of_constraints:
                    constraints_left = 0
                    while not end_of_constraints:
                        constraints_left += 1
                        try:
                            next(constraint_generator)
                        except StopIteration:
                            end_of_constraints = True
                    msg = "At least {} more inputs expected.".format(constraints_left)
                    error = CheckerError(msg)
                    line_errors[line_number].append(error)

        class Scope(Enum):
            """Scope type. Either ``Branch`` or ``Loop``."""
            Branch = 0
            Loop = 1

        def __init__(self, precursory: State = None):
            super().__init__(AssumptionState.InputStack.InputLattice, dict())
            State.__init__(self, precursory)
            self._scopes = list()  # stack of scope types

        @property
        def scopes(self):
            """Current stack of scope types."""
            return self._scopes

        @property
        def scope(self):
            """Current scope type."""
            return self._scopes[-1]

        def __repr__(self):
            return "\n---\n".join(map(repr, reversed(self.stack)))

        @copy_docstring(Stack.push)
        def push(self) -> 'AssumptionState.InputStack':
            self.stack.append(AssumptionState.InputStack.InputLattice())
            return self

        @copy_docstring(Stack.pop)
        def pop(self) -> 'AssumptionState.InputStack':
            current: AssumptionState.InputStack.InputLattice = self.stack.pop()
            self.lattice.record(current)
            return self

        @copy_docstring(State._assign)
        def _assign(self, left: Expression, right: Expression) -> 'AssumptionState.InputStack':
            raise RuntimeError("Unexpected assignment in a backward analysis!")

        @copy_docstring(State._assume)
        def _assume(self, condition: Expression) -> 'AssumptionState.InputStack':
            loop = AssumptionState.InputStack.Scope.Loop
            if not self.is_bottom() and self.scope == loop:      # the current scope is a loop
                negation_free_normal_expression = NegationFreeNormalExpression()
                normal = negation_free_normal_expression.visit(condition)
                if isinstance(normal, BinaryComparisonOperation):
                    in_op = BinaryComparisonOperation.Operator.In
                    notin_op = BinaryComparisonOperation.Operator.NotIn
                    if normal.operator == in_op or normal.operator == notin_op:
                        # the condition is ``... in range(...)`` or ``... not in range(...)``
                        if isinstance(normal.right, Range):
                            self.lattice.repeat(normal.right.stop)
                            return self
                self.lattice.top()      # default to the star constraint ★
            return self

        @copy_docstring(State.enter_if)
        def enter_if(self) -> 'AssumptionState.InputStack':
            if self.is_bottom() or self.is_top():
                return self
            self.scopes.append(AssumptionState.InputStack.Scope.Branch)
            return self.push()

        @copy_docstring(State.exit_if)
        def exit_if(self) -> 'AssumptionState.InputStack':
            if self.is_bottom() or self.is_top():
                return self
            _ = self.scopes.pop()
            return self.pop()

        @copy_docstring(State.enter_loop)
        def enter_loop(self) -> 'AssumptionState.InputStack':
            if self.is_bottom() or self.is_top():
                return self
            self.scopes.append(AssumptionState.InputStack.Scope.Loop)
            return self.push()

        @copy_docstring(State.exit_loop)
        def exit_loop(self) -> 'AssumptionState.InputStack':
            if self.is_bottom() or self.is_top():
                return self
            _ = self.scopes.pop()
            return self.pop()

        @copy_docstring(State._output)
        def _output(self, output: Expression) -> 'AssumptionState.InputStack':
            return self  # nothing to be done

        @copy_docstring(State._substitute)
        def _substitute(self, left: Expression, right: Expression) -> 'AssumptionState.InputStack':
            if isinstance(left, VariableIdentifier):
                replacement = AssumptionState.InputStack.InputReplacement(self.pp)
                replaced: Expression = replacement.visit(right)
                for i, lattice in enumerate(self.stack):
                    self.stack[i] = lattice.replace(left, replaced)
                return self
            raise NotImplementedError(f"Substitution of {left.__class__.__name__} is unsupported!")

        def record(self, constraint: InputLattice.InputConstraint) -> 'AssumptionState.InputStack':
            """Record a constraint on the input data.

            :param constraint: constraint to be recorded
            :return: current stack modified to record the constraint
            """
            self.lattice.record(constraint)
            return self

        # input replacement

        class InputReplacement(ExpressionVisitor):
            """Visitor that replaces any occurrence of an input (sub)expression
            with a fresh variable identifier that depends on a given program point.

            Example::

                input() - 3 * input()

            given the program point [line:L, column:C] becomes::

                L.1 - 3 * L.2
            """

            def __init__(self, pp: ProgramPoint):
                self._pp = pp
                self._nonce = 0

            @property
            def pp(self):
                return self._pp

            @property
            def nonce(self):
                self._nonce += 1
                return self._nonce

            @copy_docstring(ExpressionVisitor.visit_Literal)
            def visit_Literal(self, expr: Literal):
                return Literal(expr.typ, expr.val)

            @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
            def visit_VariableIdentifier(self, expr: VariableIdentifier):
                return VariableIdentifier(expr.typ, expr.name)

            @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
            def visit_LengthIdentifier(self, expr: LengthIdentifier):
                return LengthIdentifier(expr.variable)

            @copy_docstring(ExpressionVisitor.visit_ListDisplay)
            def visit_ListDisplay(self, expr: ListDisplay):
                items = [self.visit(item) for item in expr.items]
                return ListDisplay(expr.typ, items)

            @copy_docstring(ExpressionVisitor.visit_AttributeReference)
            def visit_AttributeReference(self, expr: AttributeReference):
                target = self.visit(expr.target)
                return AttributeReference(expr.typ, target, expr.attribute)

            @copy_docstring(ExpressionVisitor.visit_Subscription)
            def visit_Subscription(self, expr: Subscription):
                target = self.visit(expr.target)
                key = self.visit(expr.key)
                return AttributeReference(expr.typ, target, key)

            @copy_docstring(ExpressionVisitor.visit_Slicing)
            def visit_Slicing(self, expr: Slicing):
                target = self.visit(expr.target)
                lower = self.visit(expr.lower)
                upper = self.visit(expr.upper)
                stride = self.visit(expr.stride) if expr.stride else None
                return Slicing(expr.typ, target, lower, upper, stride)

            @copy_docstring(ExpressionVisitor.visit_Input)
            def visit_Input(self, expr: Input):
                name = "{}.{}".format(self.pp.line, self.nonce)
                return VariableIdentifier(expr.typ, name)

            @copy_docstring(ExpressionVisitor.visit_Range)
            def visit_Range(self, expr: Range):
                start = self.visit(expr.start)
                stop = self.visit(expr.stop)
                step = self.visit(expr.step)
                return Range(expr.typ, start, stop, step)

            @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
            def visit_UnaryArithmeticOperation(self, expr: UnaryArithmeticOperation):
                expression = self.visit(expr.expression)
                return UnaryArithmeticOperation(expr.typ, expr.operator, expression)

            @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
            def visit_UnaryBooleanOperation(self, expr: UnaryBooleanOperation):
                expression = self.visit(expr.expression)
                return UnaryBooleanOperation(expr.typ, expr.operator, expression)

            @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
            def visit_BinaryArithmeticOperation(self, expr: BinaryArithmeticOperation):
                left = self.visit(expr.left)
                right = self.visit(expr.right)
                return BinaryArithmeticOperation(expr.typ, left, expr.operator, right)

            @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
            def visit_BinaryBooleanOperation(self, expr: BinaryBooleanOperation):
                left = self.visit(expr.left)
                right = self.visit(expr.right)
                return BinaryBooleanOperation(expr.typ, left, expr.operator, right)

            @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
            def visit_BinaryComparisonOperation(self, expr: BinaryComparisonOperation):
                left = self.visit(expr.left)
                right = self.visit(expr.right)
                return BinaryComparisonOperation(expr.typ, left, expr.operator, right)

    def __init__(self, states: List[Type[InputMixin]],
                 arguments: Dict[Type, Dict[str, Any]] = defaultdict(lambda: dict()),
                 precursory: State = None):
        super().__init__(precursory)
        self._states = [state(**arguments[state]) for state in states]
        self._stack = AssumptionState.InputStack()

    @property
    def states(self):
        """Current list of constraining states."""
        return self._states

    @property
    def stack(self):
        """Current stack of assumptions on the input data."""
        return self._stack

    def __repr__(self):
        return "{}||{}".format(self.states, self.stack)

    @copy_docstring(State.bottom)
    def bottom(self) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.bottom()
        self.stack.bottom()
        return self

    @copy_docstring(State.top)
    def top(self) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.top()
        self.stack.top()
        return self

    @copy_docstring(State.is_bottom)
    def is_bottom(self) -> bool:
        return any(state.is_bottom() for state in self.states) or self.stack.is_bottom()

    @copy_docstring(State.is_top)
    def is_top(self) -> bool:
        return all(state.is_top() for state in self.states) and self.stack.is_top()

    @copy_docstring(State._less_equal)
    def _less_equal(self, other: 'AssumptionState') -> bool:
        states = all(state.less_equal(other.states[i]) for i, state in enumerate(self.states))
        return states and self.stack.less_equal(other.stack)

    @copy_docstring(State._join)
    def _join(self, other: 'AssumptionState') -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.join(other.states[i])
        self.stack.join(other.stack)
        return self

    @copy_docstring(State._meet)
    def _meet(self, other: 'AssumptionState'):
        for i, state in enumerate(self.states):
            self.states[i] = state.meet(other.states[i])
        self.stack.meet(other.stack)
        return self

    @copy_docstring(State._widening)
    def _widening(self, other: 'AssumptionState'):
        for i, state in enumerate(self.states):
            self.states[i] = state.widening(other.states[i])
        self.stack.widening(other.stack)
        return self

    @copy_docstring(State._assign)
    def _assign(self, left: Expression, right: Expression) -> 'AssumptionState':
        raise RuntimeError("Unexpected assignment in a backward analysis!")

    @copy_docstring(State._assume)
    def _assume(self, condition: Expression) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.assume({condition})
        self.stack.assume({condition})
        return self

    @copy_docstring(State.before)
    def before(self, pp: ProgramPoint, precursory: Optional['State']) -> 'AssumptionState':
        super().before(pp, precursory)
        for i, state in enumerate(self.states):
            self.states[i] = state.before(pp, precursory)
        self.stack.before(pp, precursory)
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.enter_if()
        self.stack.enter_if()
        return self

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.exit_if()
        self.stack.exit_if()
        return self

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.enter_loop()
        self.stack.enter_loop()
        return self

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.exit_loop()
        self.stack.exit_loop()
        return self

    @copy_docstring(State._output)
    def _output(self, output: Expression) -> 'AssumptionState':
        for i, state in enumerate(self.states):
            self.states[i] = state.output({output})
        self.stack.output({output})
        return self

    @copy_docstring(State._substitute)
    def _substitute(self, left: Expression, right: Expression) -> 'AssumptionState':
        # perform the substitution on each individual state
        for i, state in enumerate(self.states):
            self.states[i] = state.substitute({left}, {right})
        # retrieve the constraints imposed on the input data...
        retrieved = zip(*[state.retrieve() for state in self.states])
        # ...and record them on the stack
        for constraint in retrieved:
            self.stack.record((self.pp, constraint))
        # perform the substitution on the stack
        self.stack.substitute({left}, {right})
        return self


class TypeQuantityAssumptionState(AssumptionState):
    """Type+quantity assumption analysis state.
    An element of the type+quantity assumption abstract domain.

    Reduced product of type and quantity constraining states,
    which respectively collect constraints on the type and sign of values of the program variables
    and (indirectly) on the input data, and a stack of assumptions on the input data,
    which (directly) constraints the input data read from the current program point.

    .. document private methods
    .. automethod:: TypeQuantityAssumptionState._assume
    .. automethod:: TypeQuantityAssumptionState._substitute
    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        from lyra.abstract_domains.assumption.type_domain import TypeState
        from lyra.abstract_domains.assumption.quantity_domain import QuantityState
        states = [TypeState, QuantityState]
        arguments = defaultdict(lambda: {'variables': variables})
        super().__init__(states, arguments, precursory)


class TypeRangeAssumptionState(AssumptionState):
    """Type+range assumption analysis state.
    An element of the type+range assumption abstract domain.

    Reduced product of type and range constraining states,
    which respectively collect constraints on the type and range of values of the program variables
    and (indirectly) on the input data, and a stack of assumptions on the input data,
    which (directly) constraints the input data read from the current program point.

    .. document private methods
    .. automethod:: AssumptionState._assume
    .. automethod:: AssumptionState._substitute
    """

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        from lyra.abstract_domains.assumption.type_domain import TypeState
        from lyra.abstract_domains.assumption.range_domain import RangeState
        states = [TypeState, RangeState]
        arguments = defaultdict(lambda: {'variables': variables})
        super().__init__(states, arguments, precursory)


class OctagonStringAssumptionState(AssumptionState):

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        from lyra.abstract_domains.assumption.octagons_domain import OctagonState
        from lyra.abstract_domains.assumption.type_domain import TypeState
        from lyra.abstract_domains.assumption.alphabet_domain import AlphabetState
        states = [TypeState, OctagonState, AlphabetState]
        arguments = defaultdict(lambda: {'variables': variables})
        super().__init__(states, arguments, precursory)
