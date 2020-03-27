"""
Type Abstract Domain
====================

Non-relational abstract domain to be used for **input data assumption analysis**.
The set of possible values of a program variable in a state is represented as a type.

:Authors: Caterina Urban and Madelin Schumacher
"""
from collections import defaultdict
from copy import deepcopy
from enum import IntEnum
from functools import reduce
from typing import Set

from lyra.abstract_domains.assumption.assumption_domain import InputMixin, JSONMixin
from lyra.abstract_domains.lattice import BottomMixin, ArithmeticMixin, SequenceMixin
from lyra.abstract_domains.state import State, StateWithSummarization
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, ExpressionVisitor, Literal, \
    Input, ListDisplay, Range, AttributeReference, Subscription, Slicing, \
    UnaryArithmeticOperation, BinaryArithmeticOperation, LengthIdentifier, TupleDisplay, \
    SetDisplay, DictDisplay, BinarySequenceOperation, BinaryComparisonOperation, Keys, Values, \
    KeysIdentifier, ValuesIdentifier
from lyra.core.types import LyraType, BooleanLyraType, IntegerLyraType, FloatLyraType, \
    StringLyraType, ListLyraType, SequenceLyraType, SetLyraType, TupleLyraType, DictLyraType, \
    ContainerLyraType
from lyra.core.utils import copy_docstring


class TypeLattice(BottomMixin, ArithmeticMixin, SequenceMixin, JSONMixin):
    """Type Lattice::

        String
          |
        Float
          |
        Integer
          |
        Boolean
          |
          ⊥

    The default lattice element is ``String``.

    Let S be the set of all possible strings. We define F ⊆ S, I ⊆ F, B ⊆ I to be the sets of
    all possible strings that can be interpreted as floating-point numbers
    (i.e., F = { 2.35, ..., 9.345, ...}), integers (i.e., I = { -3, ..., 15, ...}),
    and booleans (i.e., B = { 0, 1 }), respectively.
    The concretization function Ɣ: TypeLattice -> 𝒫(S) is defined as follows::

        Ɣ(String) = S
        Ɣ(Float) = F
        Ɣ(Integer) = I
        Ɣ(Boolean) = B
        Ɣ(⊥) = ∅

    .. note::
        One might want to have Ɣ(Boolean) = { 'True', 'False' }. This, however, would yield
        the following different lattice structure::

                   String
                 /        \\
                /        Float
            Boolean        |
                 \\      Integer
                  \\      /
                      ⊥

        which is not compatible with subtyping between boolean and integer types in Python.

    .. document private methods
    .. automethod:: TypeLattice._less_equal
    .. automethod:: TypeLattice._meet
    .. automethod:: TypeLattice._join
    .. automethod:: TypeLattice._widening
    """
    class Status(IntEnum):
        """Type status.

        The current lattice element can be:

        * ``String``: String type

        * ``Float``: Float type

        * ``Integer`` Integer type

        * ``Boolean``: Boolean type
        """
        String = 3
        Float = 2
        Integer = 1
        Boolean = 0

    def __init__(self, type_status: Status = Status.String):
        super().__init__()
        self._element = type_status

    @classmethod
    def from_lyra_type(cls, lyra_type: LyraType):
        return cls(resolve(lyra_type))

    @property
    def element(self):
        """Current lattice element.

        :return: the current lattice element if the type is not bottom, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        return self._element

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return self.element.name

    def boolean(self) -> 'TypeLattice':
        """Integer lattice element.

        :return: current lattice element modified to be the boolean lattice element

        The integer lattice element is ``Boolean``
        """
        return self._replace(TypeLattice(TypeLattice.Status.Boolean))

    def integer(self) -> 'TypeLattice':
        """Integer lattice element.

        :return: current lattice element modified to be the integer lattice element

        The integer lattice element is ``Integer``
        """
        return self._replace(TypeLattice(TypeLattice.Status.Integer))

    def float(self) -> 'TypeLattice':
        """Float lattice element.

        :return: current lattice element modified to be the float lattice element

        The float lattice element is ``Float``.
        """
        return self._replace(TypeLattice(TypeLattice.Status.Float))

    @copy_docstring(BottomMixin.top)
    def top(self) -> 'TypeLattice':
        """The top lattice element is ``String``."""
        return self._replace(TypeLattice())

    def is_boolean(self) -> bool:
        """Test whether the lattice element is boolean.

        :return: whether the lattice element is ``Boolean``
        """
        return self.element == TypeLattice.Status.Boolean

    def is_integer(self) -> bool:
        """Test whether the lattice element is integer.

        :return: whether the lattice element is ``Integer``
        """
        return self.element == TypeLattice.Status.Integer

    def is_float(self) -> bool:
        """Test whether the lattice element is float.

        :return: whether the lattice element is ``Float``
        """
        return self.element == TypeLattice.Status.Float

    @copy_docstring(BottomMixin.is_top)
    def is_top(self) -> bool:
        return self.element == TypeLattice.Status.String

    @copy_docstring(BottomMixin._less_equal)
    def _less_equal(self, other: 'TypeLattice') -> bool:
        return self.element <= other.element

    @copy_docstring(BottomMixin._join)
    def _join(self, other: 'TypeLattice') -> 'TypeLattice':
        return self._replace(TypeLattice(max(self.element, other.element)))

    @copy_docstring(BottomMixin._meet)
    def _meet(self, other: 'TypeLattice'):
        return self._replace(TypeLattice(min(self.element, other.element)))

    @copy_docstring(BottomMixin._widening)
    def _widening(self, other: 'TypeLattice'):
        return self._join(other)

    # arithmetic operations

    @copy_docstring(ArithmeticMixin._neg)
    def _neg(self) -> 'TypeLattice':
        """
        - Boolean = Integer
        - Integer = Integer
        - Float = Float
        - String = ⊥
        """
        if self.is_boolean():
            return self._replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top():
            return self.bottom()
        return self   # nothing to be done

    @copy_docstring(ArithmeticMixin._add)
    def _add(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean + Boolean = Integer
        Boolean + Integer = Integer
        Boolean + Float = Float
        Boolean + String = ⊥
        Integer + Boolean = Integer
        Integer + Integer = Integer
        Integer + Float = Float
        Integer + String = ⊥
        Float + Boolean = Float
        Float + Integer = Float
        Float + Float = Float
        Float + String = ⊥
        String + Boolean = ⊥
        String + Integer = ⊥
        String + Float = ⊥
        String + String = ⊥
        """
        if self.is_boolean() and other.is_boolean():
            return self._replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top() or other.is_top():
            return self.bottom()
        return self._replace(TypeLattice(max(self.element, other.element)))

    @copy_docstring(ArithmeticMixin._sub)
    def _sub(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean - Boolean = Integer
        Boolean - Integer = Integer
        Boolean - Float = Float
        Boolean - String = ⊥
        Integer - Boolean = Integer
        Integer - Integer = Integer
        Integer - Float = Float
        Integer - String = ⊥
        Float - Boolean = Float
        Float - Integer = Float
        Float - Float = Float
        Float - String = ⊥
        String - Boolean = ⊥
        String - Integer = ⊥
        String - Float = ⊥
        String - String = ⊥
        """
        if self.is_boolean() and other.is_boolean():
            return self._replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top() or other.is_top():
            return self.bottom()
        return self._replace(TypeLattice(max(self.element, other.element)))

    @copy_docstring(ArithmeticMixin._mult)
    def _mult(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean * Boolean = Integer
        Boolean * Integer = Integer
        Boolean * Float = Float
        Boolean * String = ⊥
        Integer * Boolean = Integer
        Integer * Integer = Integer
        Integer * Float = Float
        Integer * String = ⊥
        Float * Boolean = Float
        Float * Integer = Float
        Float * Float = Float
        Float * String = ⊥
        String * Boolean = ⊥
        String * Integer = ⊥
        String * Float = ⊥
        String * String = ⊥
        """
        if self.is_boolean() and other.is_boolean():
            return self._replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top() or other.is_top():
            return self.bottom()
        return self._replace(TypeLattice(max(self.element, other.element)))

    @copy_docstring(ArithmeticMixin._div)
    def _div(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean / Boolean = Float
        Boolean / Integer = Float
        Boolean / Float = Float
        Boolean / String = ⊥
        Integer / Boolean = Float
        Integer / Integer = Float
        Integer / Float = Float
        Integer / String = ⊥
        Float / Boolean = Float
        Float / Integer = Float
        Float / Float = Float
        Float / String = ⊥
        String / Boolean = ⊥
        String / Integer = ⊥
        String / Float = ⊥
        String / String = ⊥
        """
        if self.is_top() or other.is_top():
            return self.bottom()
        return self._replace(TypeLattice(TypeLattice.Status.Float))

    @copy_docstring(ArithmeticMixin._mod)
    def _mod(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean % Boolean = Integer
        Boolean / Integer = Integer
        Boolean / Float = Float
        Boolean / String = ⊥
        Integer / Boolean = Integer
        Integer / Integer = Integer
        Integer / Float = Float
        Integer / String = ⊥
        Float / Boolean = Float
        Float / Integer = Float
        Float / Float = Float
        Float / String = ⊥
        String / Boolean = ⊥
        String / Integer = ⊥
        String / Float = ⊥
        String / String = ⊥
        """
        if self.is_boolean() and other.is_boolean():
            return self._replace(TypeLattice(TypeLattice.Status.Integer))
        elif self.is_top() or other.is_top():
            return self.bottom()
        return self._replace(TypeLattice(max(self.element, other.element)))

    # sequence operations

    @copy_docstring(SequenceMixin._concat)
    def _concat(self, other: 'TypeLattice') -> 'TypeLattice':
        """
        Boolean + Boolean = ⊥
        Boolean + Integer = ⊥
        Boolean + Float = ⊥
        Boolean + String = ⊥
        Integer + Boolean = ⊥
        Integer + Integer = ⊥
        Integer + Float = ⊥
        Integer + String = ⊥
        Float + Boolean = ⊥
        Float + Integer = ⊥
        Float + Float = ⊥
        Float + String = ⊥
        String + Boolean = ⊥
        String + Integer = ⊥
        String + Float = ⊥
        String + String = String
        """
        if self.is_top() and other.is_top():
            return self
        return self.bottom()

    # json operations

    @copy_docstring(JSONMixin.to_json)
    def to_json(self) -> str:
        return str(self)

    @staticmethod
    @copy_docstring(JSONMixin.from_json)
    def from_json(json: str) -> 'JSONMixin':
        if json == '⊥':
            return TypeLattice().bottom()
        if json == 'Boolean':
            return TypeLattice(TypeLattice.Status.Boolean)
        elif json == 'Integer':
            return TypeLattice(TypeLattice.Status.Integer)
        elif json == 'Float':
            return TypeLattice(TypeLattice.Status.Float)
        return TypeLattice()


def resolve(typ: LyraType) -> TypeLattice.Status:
    _typ = typ
    while isinstance(_typ, (ListLyraType, TupleLyraType, SetLyraType, DictLyraType)):
        if isinstance(_typ, (ListLyraType, SetLyraType)):
            _typ = _typ.typ
        elif isinstance(_typ, TupleLyraType):
            _typ = reduce(max, map(resolve, _typ.typs), TypeLattice.Status.Boolean)
        elif isinstance(_typ, DictLyraType):
            _typ = max(resolve(_typ.key_typ), resolve(_typ.val_typ))
    if isinstance(_typ, TypeLattice.Status):
        return _typ
    elif isinstance(_typ, BooleanLyraType):
        return TypeLattice.Status.Boolean
    elif isinstance(_typ, IntegerLyraType):
        return TypeLattice.Status.Integer
    elif isinstance(_typ, FloatLyraType):
        return TypeLattice.Status.Float
    return TypeLattice.Status.String


class TypeState(Store, StateWithSummarization, InputMixin):
    """Type assumption analysis state. An element of the type assumption abstract domain.

    Map from each program variable to the type representing its value.
    The value of all program variables is represented by their Lyra type by default.

    .. note::
        This means that, for any map m: VariableIdentifier -> TypeLattice and variable x,
        we should always have m(x) ≤ TypeLattice.from_lyra_type(x.typ)

    When reading input data, the corresponding type assumptions
    are stored in the class member ``inputs``, which is a map from each program point
    to the list of type assumptions on the inputs read at that point.

    .. note:: Program variables storing collections are abstracted via summarization.

    .. document private methods
    .. automethod:: TypeState._assume
    .. automethod:: TypeState._substitute
    """
    class Status(defaultdict):

        def __missing__(self, key):
            return {'type_status': resolve(key)}

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to the type representing its value.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: TypeLattice)
        arguments = TypeState.Status()
        super().__init__(variables, lattices, arguments)
        InputMixin.__init__(self, precursory)

    @copy_docstring(Store.is_bottom)
    def is_bottom(self) -> bool:
        """The current state is bottom if `any` non-summary variable maps to a bottom element,
        or if the length identifier of `any` summary variable maps to a bottom element."""
        for var, element in self.store.items():
            if not var.special:
                if isinstance(var.typ, (SequenceLyraType, ContainerLyraType)):
                    if element.is_bottom() and self.store[LengthIdentifier(var)].is_bottom():
                        return True
                elif element.is_bottom():
                    return True
        return False

    @copy_docstring(State._assign_variable)
    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'TypeState':
        evaluation = self._evaluation.visit(right, self, dict())
        typ = TypeLattice.from_lyra_type(left.typ)
        self.store[left] = evaluation[right].meet(typ)
        if isinstance(left.typ, DictLyraType):
            _typ = TypeLattice.from_lyra_type(left.typ.key_typ)
            typ_ = TypeLattice.from_lyra_type(left.typ.val_typ)
            if isinstance(right.typ, DictLyraType):
                self.store[KeysIdentifier(left)] = evaluation[KeysIdentifier(right)].meet(_typ)
                self.store[ValuesIdentifier(left)] = evaluation[ValuesIdentifier(right)].meet(typ_)
            else:
                self.store[KeysIdentifier(left)] = deepcopy(evaluation[right]).meet(deepcopy(typ))
                self.store[ValuesIdentifier(left)] = deepcopy(evaluation[right]).meet(deepcopy(typ))
        return self

    @copy_docstring(StateWithSummarization._assign_dictionary_subscription)
    def _assign_dictionary_subscription(self, left: Subscription, right: Expression) -> 'TypeState':
        # copy the current state
        current: TypeState = deepcopy(self)
        # perform the assignment on the copy of the current state
        target = left
        key = None
        while isinstance(target, Subscription):  # recurse to VariableIdentifier target
            key = target.key
            target = target.target
        # do self._assign_variable(target, right)
        _evaluation = self._evaluation.visit(key, self, dict())
        _typ = TypeLattice.from_lyra_type(target.typ.key_typ)
        evaluation = self._evaluation.visit(right, self, dict())
        typ = TypeLattice.from_lyra_type(target.typ)
        typ_ = TypeLattice.from_lyra_type(target.typ.val_typ)
        self.store[target] = deepcopy(evaluation[right]).join(deepcopy(_evaluation[key])).meet(typ)
        self.store[KeysIdentifier(target)] = _evaluation[key].meet(_typ)
        self.store[ValuesIdentifier(target)] = evaluation[right].meet(typ_)
        # perform a weak update on the current state
        return self.join(current)

    @copy_docstring(StateWithSummarization._weak_update)
    def _weak_update(self, variables: Set[VariableIdentifier], previous: 'TypeState'):
        for var in variables:
            self.store[var].join(previous.store[var])
        return self

    @copy_docstring(State._assume_variable)
    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_eq_comparison)
    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_noteq_comparison)
    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_lt_comparison)
    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_lte_comparison)
    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_gt_comparison)
    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_gte_comparison)
    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_is_comparison)
    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_isnot_comparison)
    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_in_comparison)
    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State._assume_notin_comparison)
    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False) -> 'TypeState':
        return self

    @copy_docstring(State.enter_if)
    def enter_if(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.exit_if)
    def exit_if(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.enter_loop)
    def enter_loop(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.exit_loop)
    def exit_loop(self) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State.forget_variable)
    def forget_variable(self, variable: VariableIdentifier) -> 'TypeState':
        self.store[variable].top()
        if isinstance(variable.typ, DictLyraType):
            self.store[KeysIdentifier(variable)].top()
            self.store[ValuesIdentifier(variable)].top()
        return self

    @copy_docstring(State.output)
    def _output(self, output: Expression) -> 'TypeState':
        return self  # nothing to be done

    @copy_docstring(State._substitute_variable)
    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'TypeState':
        # record the current value of the substituted variable
        value: TypeLattice = deepcopy(self.store[left])
        # forget the current value of the substituted variable
        typ = resolve(left.typ)
        if typ == TypeLattice.Status.Boolean:
            self.store[left].boolean()
        elif typ == TypeLattice.Status.Integer:
            self.store[left].integer()
        elif typ == TypeLattice.Status.Float:
            self.store[left].float()
        else:
            assert typ == TypeLattice.Status.String
            self.store[left].top()
        # evaluate the right-hand side bottom-up using the updated store and the Lyra types
        evaluation = self._evaluation.visit(right, self, dict())
        # restrict the value of the right-hand side using that of the substituted variable
        refinement = evaluation[right].meet(value)
        # refine the updated store proceeding top-down on the right-hand side
        self._refinement.visit(right, evaluation, refinement, self)

        # check whether the property ∀x. m(x) ≤ TypeLattice.from_lyra_type(x.typ) still holds
        store = self.store
        assert all(store[v].less_equal(TypeLattice.from_lyra_type(v.typ)) for v in store.keys())

        return self

    @copy_docstring(InputMixin.replace)
    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'TypeState':
        # collect the new variables appearing in the replacing expression
        variables: Set[VariableIdentifier] = set()
        for identifier in expression.ids():
            if isinstance(identifier, VariableIdentifier):
                variables.add(identifier)
        variables: Set[VariableIdentifier] = variables.difference(set(self.variables))
        if variables:  # if there are new variables appearing in the replacing expression...
            # add the new variables to the current state
            for fresh in variables:
                self.variables.append(fresh)
                self.store[fresh] = self.lattices[type(fresh.typ)](**self.arguments[type(fresh.typ)])
            # replace the given variable with the given expression
            self._substitute(variable, expression)
        return self

    @copy_docstring(InputMixin.unify)
    def unify(self, other: 'TypeState') -> 'TypeState':
        # collect the variables that differ in the current and other state
        mine = sorted(set(self.variables).difference(set(other.variables)), key=lambda x: x.name)
        theirs = sorted(set(other.variables).difference(set(self.variables)), key=lambda x: x.name)
        # replace the variables in the current state that match those in the other state
        for my_var, their_var in zip(mine, theirs):
            # the replacement only occurs when the matching variables in the other state
            # depend on a program point that is smaller than the program point on which
            # the variables in the current state depend
            if their_var.name < my_var.name:
                self.variables[self.variables.index(my_var)] = their_var
                self.store[their_var] = self.store.pop(my_var)
        # add variables only present in the other state
        for var in theirs[len(mine):]:
            self.variables.append(var)
            self.store[var] = self.lattices[type(var.typ)](**self.arguments[type(var.typ)])
        return self

    # expression evaluation

    class ExpressionEvaluation(ExpressionVisitor):
        """Visitor that performs the evaluation of an expression in the type lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = TypeLattice.from_lyra_type(expr.typ)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: VariableIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            value: TypeLattice = deepcopy(state.store[expr])
            evaluation[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr: LengthIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            value: TypeLattice = deepcopy(state.store[expr])
            evaluation[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
            return evaluation

        def visit_KeysIdentifier(self, expr: KeysIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            value: TypeLattice = deepcopy(state.store[expr])
            evaluation[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
            return evaluation

        def visit_ValuesIdentifier(self, expr: ValuesIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            value: TypeLattice = deepcopy(state.store[expr])
            evaluation[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation   # nothing to be done
            evaluated = evaluation
            value: TypeLattice = TypeLattice().bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                value = value.join(evaluated[item])
            evaluation[expr] = value
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation   # nothing to be done
            evaluated = evaluation
            value: TypeLattice = TypeLattice().bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                value = value.join(evaluated[item])
            evaluation[expr] = value
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation   # nothing to be done
            evaluated = evaluation
            value: TypeLattice = TypeLattice().bottom()
            for item in expr.items:
                evaluated = self.visit(item, state, evaluated)
                value = value.join(evaluated[item])
            evaluation[expr] = value
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation   # nothing to be done
            evaluated = evaluation
            _value: TypeLattice = TypeLattice().bottom()
            value: TypeLattice = TypeLattice().bottom()
            value_: TypeLattice = TypeLattice().bottom()
            for key in expr.keys:
                evaluated = self.visit(key, state, evaluated)
                value = value.join(evaluated[key])
                _value = _value.join(evaluated[key])
            for val in expr.values:
                evaluated = self.visit(val, state, evaluated)
                value = value.join(evaluated[val])
                value_ = value_.join(evaluated[val])
            evaluation[KeysIdentifier(expr)] = _value
            evaluation[expr] = value
            evaluation[ValuesIdentifier(expr)] = value_
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target, state, evaluation)
            if isinstance(expr.typ, DictLyraType):
                evaluated_ = self.visit(ValuesIdentifier(expr.target), state, evaluation)
                retrieved = evaluated_.get(ValuesIdentifier(expr.target), evaluated[expr.target])
                evaluation[expr] = retrieved.meet(TypeLattice.from_lyra_type(expr.typ))
            else:
                evaluation[expr] = evaluated[expr.target].meet(TypeLattice.from_lyra_type(expr.typ))
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.target, state, evaluation)
            evaluation[expr] = evaluated[expr.target].meet(TypeLattice.from_lyra_type(expr.typ))
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = TypeLattice.from_lyra_type(expr.typ)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                # same as for UnaryArithmeticOperation.Operator.Sub
                # + Boolean = Integer
                # + Integer = Integer
                # + Float = Float
                # + String = ⊥
                value: TypeLattice = deepcopy(evaluated[expr.expression]).neg()
                evaluated[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                value: TypeLattice = deepcopy(evaluated[expr.expression]).neg()
                evaluated[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated
            raise ValueError(f"Unary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).add(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).sub(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).mult(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Div:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).div(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            raise ValueError(f"Binary operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).concat(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            raise ValueError(f"Binary operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances

    # expression refinement

    class ArithmeticExpressionRefinement(ExpressionVisitor):
        """Visitor that:

        (1) refines the value of an evaluated arithmetic expression based on a given interval; and
        (2) modifies the current state based on the refined value of the arithmetic expression.
        """

        def visit(self, expr: Expression, *args, **kwargs):
            """Visit of an evaluated expression."""
            method = 'visit_' + expr.__class__.__name__
            if hasattr(self, method):
                return getattr(self, method)(expr, *args, **kwargs)
            raise NotImplementedError(
                f"Missing visitor for {expr.__class__.__name__} in {self.__class__.__qualname__}!")

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, evaluation=None, value=None, state=None):
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            state.store[expr] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for item in expr.items:
                updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for item in expr.items:
                updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for item in expr.items:
                updated = self.visit(item, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, evaluation=None, value=None, state=None):
            refined = evaluation[expr].meet(value)
            updated = state
            for key in expr.keys:
                updated = self.visit(key, evaluation, refined, updated)
            for val in expr.values:
                updated = self.visit(val, evaluation, refined, updated)
            return updated

        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, evaluation=None, value=None, state=None):
            refined = evaluation[expr]  # weak update
            state.store[expr.target] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, evaluation=None, value=None, state=None):
            refined = evaluation[expr]  # weak update
            state.store[expr.target] = refined
            return state

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, evaluation=None, value=None, state=None):
            state.record(value)
            return state    # nothing to be done

        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, state=None, evaluation=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, state=None, evaluation=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            add = UnaryArithmeticOperation.Operator.Add
            sub = UnaryArithmeticOperation.Operator.Sub
            if expr.operator == add or expr.operator == sub:
                refined = evaluation[expr].meet(value)
                val = TypeLattice(TypeLattice.Status.Integer).meet(refined)
                return self.visit(expr.expression, evaluation, val, state)
            raise ValueError(f"Unary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, evaluation=None, value=None, state=None):
            add = BinaryArithmeticOperation.Operator.Add
            sub = BinaryArithmeticOperation.Operator.Sub
            mult = BinaryArithmeticOperation.Operator.Mult
            div = BinaryArithmeticOperation.Operator.Div
            operator = expr.operator
            if operator == add or operator == sub or operator == mult or operator == div:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).meet(evaluation[expr.right])
                left = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).meet(evaluation[expr.left])
                right = self.visit(expr.right, evaluation, refinement2, left)
                return right
            raise ValueError(f"Binary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, evaluation=None, value=None, state=None):
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                refined = evaluation[expr].meet(value)
                refinement1 = deepcopy(refined).meet(evaluation[expr.right])
                left = self.visit(expr.left, evaluation, refinement1, state)
                refinement2 = deepcopy(refined).meet(evaluation[expr.left])
                right = self.visit(expr.right, evaluation, refinement2, left)
                return right
            raise ValueError(f"Binary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, evaluation=None, value=None, state=None):
            error = f"Refinement for a {expr.__class__.__name__} expression is unsupported!"
            raise ValueError(error)

    _refinement = ArithmeticExpressionRefinement()  # static class member shared between instances
