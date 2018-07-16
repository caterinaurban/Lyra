"""
Octagons Abstract Domain
========================

Relational abstract domain to be used for **octagons analysis**
TODO
:Authors: Radwa Sherif Abdelbar and Gagandeep Singh
"""
import sys
from copy import deepcopy
from ctypes import util
from typing import List

from elina.python_interface.elina_abstract0 import *
from elina.python_interface.elina_coeff import *
from elina.python_interface.elina_dimension import *
from elina.python_interface.elina_lincons0 import *
from elina.python_interface.elina_linexpr0 import *
from elina.python_interface.elina_linexpr0_h import *
from elina.python_interface.elina_scalar import *
from elina.python_interface.elina_scalar_h import *
from elina.python_interface.opt_oct import *
from lyra.abstract_domains.assumption.assumption_domain import InputMixin
from lyra.abstract_domains.lattice import Lattice
from lyra.abstract_domains.state import State
from lyra.core.expressions import Identifier, VariableIdentifier, Expression, ExpressionVisitor, Literal, \
    UnaryArithmeticOperation, UnaryBooleanOperation, BinaryBooleanOperation, BinaryComparisonOperation, \
    BinaryArithmeticOperation, NegationFreeNormalExpression
from lyra.core.statements import ProgramPoint
from lyra.core.types import IntegerLyraType, FloatLyraType, BooleanLyraType
from lyra.core.utils import copy_docstring

_elina_manager = opt_oct_manager_alloc()


class OctagonLattice(Lattice):

    def __init__(self, variable_names: dict, indexes: dict, dimensions: int, elina_abstract = None):
        super().__init__()
        self._dimensions = dimensions
        self._variable_names = variable_names
        self._indexes = indexes
        dict_symmetry(variable_names, indexes)
        self._elina_abstract = None
        self._elina_linear_constraints = None
        top = elina_abstract0_top(_elina_manager, 0, dimensions)
        # setting property sets both the elina abstract element and elina lincons array
        self.elina_abstract = top if elina_abstract is None else elina_abstract

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def variable_names(self):
        return self._variable_names

    @property
    def indexes(self):
        return self._indexes

    @property
    def elina_abstract(self):
        return self._elina_abstract

    @property
    def elina_linear_constraints(self):
        return elina_abstract0_to_lincons_array(_elina_manager, self.elina_abstract)

    @elina_abstract.setter
    def elina_abstract(self, elina_abstract):
        self._elina_abstract = elina_abstract
        # self._elina_linear_constraints = elina_abstract0_to_lincons_array(_elina_manager, elina_abstract)

    def __repr__(self):
        if self.is_top():
            return "T"
        if self.is_bottom():
            return "⊥"
        linear_constraints = self.elina_linear_constraints
        result = []
        for j in range(linear_constraints.size):
            lincons = linear_constraints.p[j]
            # print(self.lincons_to_string(lincons))
            result.append(self.lincons_to_string(lincons))
        return f"OCT({','.join(result)})"

    @copy_docstring(Lattice.bottom)
    def bottom(self):
        bottom = elina_abstract0_bottom(_elina_manager, 0, self.dimensions)
        return self.replace(OctagonLattice(self.variable_names, self.indexes, self.dimensions, bottom))

    @copy_docstring(Lattice.top)
    def top(self):
        top = elina_abstract0_top(_elina_manager, 0, self.dimensions)
        return self.replace(OctagonLattice(self.variable_names, self.indexes, self.dimensions, top))

    @copy_docstring(Lattice.is_bottom)
    def is_bottom(self) -> bool:
        return elina_abstract0_is_bottom(_elina_manager, self.elina_abstract)

    @copy_docstring(Lattice.is_top)
    def is_top(self) -> bool:
        return elina_abstract0_is_top(_elina_manager, self.elina_abstract)

    @copy_docstring(Lattice._less_equal)
    def _less_equal(self, other: 'OctagonLattice') -> bool:
        return elina_abstract0_is_leq(_elina_manager, self.elina_abstract, other.elina_abstract)

    @copy_docstring(Lattice._join)
    def _join(self, other: 'OctagonLattice') -> 'OctagonLattice':
        elina_abstract = elina_abstract0_join(_elina_manager, False, self.elina_abstract, other.elina_abstract)
        return self.replace(OctagonLattice(self.variable_names, self.indexes, self.dimensions, elina_abstract))

    @copy_docstring(Lattice._meet)
    def _meet(self, other: 'OctagonLattice'):
        elina_abstract = elina_abstract0_meet(_elina_manager, False, self.elina_abstract, other.elina_abstract)
        return self.replace(OctagonLattice(self.variable_names, self.indexes, self.dimensions, elina_abstract))

    @copy_docstring(Lattice._widening)
    def _widening(self, other: 'OctagonLattice'):
        return self._join(other)

    def replace_variable(self, variable: Identifier, pp: ProgramPoint):
        # input_varname = f"id{pp.line}"
        # for idx, varname in self.variable_names.items():
        #     if varname == variable.name:
        #         self.variable_names[idx] = input_varname
        #         self.indexes[input_varname] = idx
        pass

    @copy_docstring(Lattice.copy)
    def copy(self):
        abstract = elina_abstract0_copy(_elina_manager, self.elina_abstract)
        return OctagonLattice(deepcopy(self.variable_names), deepcopy(self.indexes), self.dimensions, abstract)

    def to_json(self):
        js = dict()
        js["dimensions"] = self.dimensions
        js["variable_names"] = self.variable_names
        js["indexes"] = self.indexes
        if self.is_bottom():
            js["lincons_array"] = "⊥"
        if self.is_top():
            js["lincons_array"] = "T"
        js["lincons_array"] = []
        for i in range(self.elina_linear_constraints.size):
            lincons = self.elina_linear_constraints.p[i]
            lincons_json = dict()
            lincons_json["variables"] = []
            lincons_json["signs"] = []
            for j in range(lincons.linexpr0.contents.size):
                linterm = lincons.linexpr0.contents.p.linterm[j]
                coeff = linterm.coeff
                lincons_json["variables"].append(linterm.dim)
                coeff_val = elina_scalar_sgn(coeff.val.scalar)
                lincons_json["signs"].append(coeff_val)
            lincons_json["constraint_type"] = lincons.constyp
            lincons_json["constant"] = lincons.linexpr0.contents.cst.val.scalar.contents.val.dbl
            js["lincons_array"].append(lincons_json)
        return js

    # ================ HELPER FUNCTIONS ====================
    def project(self, dim: int):
        """
        Performs the project/forget operation of the given dimension
        :param
        """
        libc = CDLL(util.find_library('c'))
        cstdout = c_void_p.in_dll(libc, 'stdout')
        print("BEFORE PROJECTION", dim)
        elina_abstract0_fprint(cstdout, _elina_manager, self.elina_abstract, None)
        abstract = elina_abstract0_forget_array(_elina_manager, False, self.elina_abstract, ElinaDim(dim), 1, False)
        print("AFTER PROJECTION")
        elina_abstract0_fprint(cstdout, _elina_manager, abstract, None)
        return self.replace(OctagonLattice(deepcopy(self.variable_names), deepcopy(self.indexes), self.dimensions, abstract))

    def add_dimension(self, variable_name: str):
        dimchange = elina_dimchange_alloc(0, 1)
        dimchange.contents.dim[0] = self.dimensions
        # add the new dimension to Elina
        abstract = elina_abstract0_add_dimensions(_elina_manager, False, self.elina_abstract, dimchange, False)
        # update dictionary of Elina with the new variable
        variable_names = deepcopy(self.variable_names)
        indexes = deepcopy(self.indexes)
        variable_names[self.dimensions] = variable_name
        indexes[variable_name] = self.dimensions
        # update the number of dimensions of Elina
        dimensions = self.dimensions + 1
        return self.replace(OctagonLattice(variable_names, indexes, dimensions, abstract))

    def handle_input(self, dim:int, pp: int):
        print("OCTAGON HANDLE INPUT", dim, pp)
        new_lattice = self.copy()
        self.project(dim)
        input_varname = f"id{pp}"
        if not input_varname in new_lattice.indexes:
            new_lattice.add_dimension(input_varname)

        dimperm = elina_dimperm_alloc(new_lattice.dimensions)
        for i in range(new_lattice.dimensions):
            dimperm.contents.dim[i] = i
        input_index = new_lattice.indexes[input_varname]
        dimperm.contents.dim[dim] = input_index
        dimperm.contents.dim[input_index] = dim
        abstract = elina_abstract0_permute_dimensions(_elina_manager, False, new_lattice.elina_abstract, dimperm)
        new_lattice.replace(OctagonLattice(deepcopy(new_lattice.variable_names), deepcopy(new_lattice.indexes), new_lattice.dimensions, abstract))
        # new_lattice.project(dim)
        return new_lattice

    def lincons_to_string(self, lincons, id_input_line=None):
        """
        Forms a string representation of an Elina linear constraint
        :param lincons: Linear constraint to be
        represented.
        :param id_input_line: optional dictionary to use for mapping indexes to input lines. Default is
        self.variable_names.
        :return:
        """
        # print("LINEAR CONSTRAINT")
        # elina_lincons0_print(lincons, None)
        # print()
        string = ""
        for i in range(lincons.linexpr0.contents.size):
            linterm = lincons.linexpr0.contents.p.linterm[i]
            coeff = linterm.coeff
            coeff_val = elina_scalar_sgn(coeff.val.scalar)
            # print(coeff.val.scalar.contents.discr==ELINA_SCALAR_MPQ)
            string += (" +" if coeff_val >= 0 else " -")
            string += " " if i > 0 else ""
            if coeff_val not in [1, -1]:
                string += str(coeff_val) + "*"
            if id_input_line is None:
                string += (self.variable_names[linterm.dim])
            else:
                varname = self.variable_names[linterm.dim]
                string += f"line {id_input_line[int(varname[2:])]}"
        const_dbl = lincons.linexpr0.contents.cst.val.scalar.contents.val.dbl
        if const_dbl >= 0:
            string += ' + '
        else:
            string += ' - '
        string += str(abs(const_dbl))
        if lincons.constyp == ElinaConstyp.ELINA_CONS_SUPEQ:
            string += " >= "
        elif lincons.constyp == ElinaConstyp.ELINA_CONS_SUP:
            string += " > "
        elif lincons.constyp == ElinaConstyp.ELINA_CONS_EQ:
            string += " = "
        string += "0"
        # print("FUNCTION OUTPUT", string)
        return string

    @staticmethod
    def create_linear_expression(indexes: List[int], coefficients: List[int], constant: int):
        if len(indexes) != len(coefficients):
            raise ValueError("var and sign should have the same length")
        size = len(indexes)
        linexpr = elina_linexpr0_alloc(ElinaLinexprDiscr.ELINA_LINEXPR_SPARSE, size)
        # print(f"LINEXP{indexes}, {coefficients}, {constant}")
        if constant is not None:
            cst = pointer(linexpr.contents.cst)
            # set the constant of the expression to c
            elina_scalar_set_double(cst.contents.val.scalar, float(constant))
        # set the variables and coefficients (signs) of the linear expression
        for i in range(size):
            linterm = pointer(linexpr.contents.p.linterm[i])
            linterm.contents.dim = ElinaDim(indexes[i])
            coeff = pointer(linterm.contents.coeff)
            elina_scalar_set_double(coeff.contents.val.scalar, float(coefficients[i]))
        # elina_linexpr0_print(linexpr, None)
        # print()
        return linexpr

    def add_linear_constraint(self, indexes: List[int], coefficients: List[int], constant: int, constraint_type: 'BinaryComparisonOperation.Operator'):
        """
        Adds a new linear constraint represented by a list of variables and their coefficients. **Important note**:
        NegationFreeNormalExpression creates constraints of the form 'variables + constant <= 0', while ELINA
        supports constraints of the form 'variables + constant>= 0'.
        :param constraint_type:
        :param indexes:
        :param coefficients:
        :param constant:
        :return:
        """
        # assert constraint_type == BinaryComparisonOperation.Operator.LtE, f"Linear constraint was not normalized " \
        #                                                                   "properly. "
        # create elina linear expression
        linexpr = OctagonLattice.create_linear_expression(indexes, coefficients, constant)
        # print("LINEAR EXPRESSION")
        # elina_linexpr0_print(linexpr, None)
        # print()
        # create elina linear constraint array of size
        lincons_array = elina_lincons0_array_make(1)
        # the constraint uses the linear expression with constraint type of '>=' always
        lincons_array.p[0].constyp = ElinaConstyp.ELINA_CONS_SUPEQ
        lincons_array.p[0].linexpr0 = linexpr
        # print("LINEAR CONSTRAINT TO MEET WITH TOP")
        # elina_lincons0_array_print(lincons_array, None)

        # print(self.lincons_to_string(lincons_array.p[0]))
        libc = CDLL(util.find_library('c'))
        cstdout = c_void_p.in_dll(libc, 'stdout')
        # create lattice element representing the linear constraint
        top = elina_abstract0_top(_elina_manager, 0, self.dimensions)
        # print('****')
        # print("ABSTRACT ELEMENT TOP")
        # elina_abstract0_fprint(cstdout, _elina_manager, top, None)
        # print('****')
        # abstract = elina_abstract0_meet_lincons_array(_elina_manager, False, top, lincons_array)
        abstract = elina_abstract0_meet_lincons_array(_elina_manager, False, top, lincons_array)
        # print("****")
        # print("ABSTRACT ELEMENT AFTER MEET")
        # elina_abstract0_fprint(cstdout, _elina_manager, abstract, None)
        # print('****')
        linear_constraint_element = OctagonLattice(deepcopy(self.variable_names), deepcopy(self.indexes), self.dimensions, abstract)
        # print("CONSTRAINT LATTICE")
        # print(linear_constraint_element)
        # print('------------------------')

        # perform meet between the linear constraint and the already existing constraints
        return self.meet(linear_constraint_element)

    def substitution(self, subs_variable: str, variables:List[str], coefficients: List[int], constant: int):
        subs_index = self.indexes[subs_variable]
        indexes = [self.indexes[var] for var in variables]
        linexpr = OctagonLattice.create_linear_expression(indexes, coefficients, constant)
        abstract = elina_abstract0_substitute_linexpr(_elina_manager, False, self.elina_abstract, ElinaDim(subs_index), linexpr, None)
        return self.replace(OctagonLattice(deepcopy(self.variable_names), deepcopy(self.indexes), self.dimensions, abstract))


_normalizer = NegationFreeNormalExpression()  # puts comparison expressions in the form expr <= 0


class ConditionEvaluator(ExpressionVisitor):
    """
    """

    def visit_Literal(self, expr: 'Literal', *args):
        if expr.typ == IntegerLyraType() or expr.typ is FloatLyraType() or expr.typ is BooleanLyraType():
            type_cast = {
                'int': int,
                'float': float,
                'bool': bool
            }
            #TODO handle bools
            return [], [], type_cast[str(expr.typ)](expr.val)
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_Input(self, expr: 'Input', *args):
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_VariableIdentifier(self, expr: 'VariableIdentifier', *args):
        if expr.typ in [FloatLyraType(), IntegerLyraType(), BooleanLyraType()]:
            return [expr.name], [1], 0
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_LengthIdentifier(self, expr: 'VariableIdentifier', *args):
        if expr.typ in [FloatLyraType(), IntegerLyraType(), BooleanLyraType()]:
            return [expr.name], [1], 0
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_ListDisplay(self, expr: 'ListDisplay'):
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")


    def visit_Range(self, expr: 'Range'):
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")


    def visit_Split(self, expr: 'Split'):
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_AttributeReference(self, expr: 'AttributeReference'):
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_Subscription(self, expr: 'Subscription'):
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_Slicing(self, expr: 'Slicing'):
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")


    def visit_UnaryArithmeticOperation(self, expr: 'UnaryArithmeticOperation'):
        coeff = 1 if expr.operator == UnaryArithmeticOperation.Operator.Add else -1
        expr = expr.expression
        variables, coefficients, constant = self.visit(expr)
        return variables, list(map(lambda x: coeff * x), coefficients), coeff * constant

    def visit_UnaryBooleanOperation(self, expr: 'UnaryBooleanOperation', lattice_element: 'OctagonLattice'):
        operator = expr.operator
        expr = expr.expression
        if operator == UnaryBooleanOperation.Operator.Neg:
            if isinstance(expr, BinaryBooleanOperation):
                left = UnaryBooleanOperation(expr.left.typ, UnaryBooleanOperation.Operator.Neg, expr.left)
                operator = expr.operator.reverse_operator()
                right = UnaryBooleanOperation(expr.right, UnaryBooleanOperation.Operator.Neg, expr.right)
                expr = BinaryBooleanOperation(expr.typ, left, operator, right)
                return self.visit(expr, lattice_element)
            elif isinstance(expr, BinaryComparisonOperation):
                operator = expr.operator.reverse_operator()
                expr = BinaryComparisonOperation(expr.typ, expr.left, operator, expr.right)
                return self.visit(expr, lattice_element)
            elif isinstance(expr, UnaryBooleanOperation):
                if expr.operator == UnaryBooleanOperation.Operator.Neg:
                    return self.visit(expr.expression, lattice_element)
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_BinaryArithmeticOperation(self, expr: 'BinaryArithmeticOperation', lattice_element: 'OctagonLattice'):
        coeff = None
        variables1, coefficients1, constant1 = self.visit(expr.left, lattice_element)
        variables2, coefficients2, constant2 = self.visit(expr.right, lattice_element)
        if expr.operator == BinaryArithmeticOperation.Operator.Add:
            coeff = 1
        elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
            coeff = -1

        if expr.operator in [BinaryArithmeticOperation.Operator.Add, BinaryArithmeticOperation.Operator.Sub]:
            variables = variables1 + variables2
            coefficients = coefficients1 + list(map(lambda x: coeff * x, coefficients2))
            constant = constant1 + coeff * constant2
            return variables, coefficients, constant

        if expr.operator == BinaryArithmeticOperation.Operator.Mult:
            if len(variables1) == len(variables2) == 0:
                return [], [], constant1 * constant2
            elif len(variables1) > 0 and len(variables2) == 0:
                return variables1, list(map(lambda x: x * constant2, coefficients1)), constant1 * constant2
            elif len(variables2) > 0 and len(variables1) == 0:
                return variables2, list(map(lambda x: x * constant1, coefficients2)), constant1 * constant2
        # TODO handle y/x --> x != 0
        if expr.operator == BinaryArithmeticOperation.Operator.Div:
            if len(variables1) == len(variables2) == 0:
                if constant2 != 0:
                    return [], [], constant1 / constant2
                raise ZeroDivisionError
            elif len(variables1) > 0 and len(variables2) == 0:
                if constant2 != 0:
                    return variables1, list(map(lambda x: x / constant2, coefficients1)), constant1 / constant2
                raise ZeroDivisionError
            elif len(variables2) > 0:
                denominator = BinaryComparisonOperation(expr.left.typ, expr.left, BinaryComparisonOperation.Operator.NotEq, Literal(IntegerLyraType, "0"))
                self.visit(denominator, lattice_element)
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_BinaryComparisonOperation(self, expr: 'BinaryComparisonOperation', lattice_element: 'OctagonLattice'):
        normal_expr = _normalizer.visit(expr)  # in the form expr <= 0
        if expr.operator in [BinaryComparisonOperation.Operator.NotEq, BinaryComparisonOperation.Operator.LtE, BinaryComparisonOperation.Operator.Lt, BinaryComparisonOperation.Operator.Eq, BinaryComparisonOperation.Operator.GtE, BinaryComparisonOperation.Operator.Gt]:
            if isinstance(normal_expr, BinaryComparisonOperation):
                variables, coefficients, constant = self.visit(normal_expr.left, lattice_element)
                indexes = [lattice_element.indexes[var] for var in variables]
                coefficients = list(map(lambda x: -x, coefficients))
                constant *= -1
                return lattice_element.add_linear_constraint(indexes, coefficients, constant, normal_expr.operator)
            else:
                copy = lattice_element.copy()
                self.visit(normal_expr, copy)
                return copy
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")

    def visit_BinaryBooleanOperation(self, expr: 'BinaryBooleanOperation', lattice_element: 'OctagonLattice'):
        # modifies element itself
        lattice_left = lattice_element.copy()
        lattice_right = lattice_element.copy()
        self.visit(expr.left, lattice_left)
        self.visit(expr.right, lattice_right)
        if expr.operator == BinaryBooleanOperation.Operator.Or:
            return lattice_element.replace(lattice_left.join(lattice_right))
        elif expr.operator == BinaryBooleanOperation.Operator.And:
            return lattice_element.replace(lattice_left.meet(lattice_right))
        raise NotImplementedError(f"Condition evaluator for expression {expr} is not implemented.")


_evaluator = ConditionEvaluator()


class OctagonState(InputMixin):

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'InputMixin':
        pass

    def unify(self, other: 'InputMixin') -> 'InputMixin':
        pass

    def __init__(self, variables: List[VariableIdentifier]):
        super().__init__()
        self.variables = variables
        self.variables_names = {i: var.name for i, var in enumerate(self.variables)}
        self.indexes = {var.name: i for i, var in enumerate(self.variables)}
        self.lattice_element = OctagonLattice(self.variables_names, self.indexes, len(self.variables))

    def __repr__(self):
        return repr(self.lattice_element)

    def bottom(self):
        self.lattice_element.bottom()
        return self

    def top(self):
        self.lattice_element.top()
        return self

    def is_bottom(self) -> bool:
        return self.lattice_element.is_bottom()

    def is_top(self) -> bool:
        return self.lattice_element.is_top()

    def _less_equal(self, other: 'OctagonState') -> bool:
        return self.lattice_element.less_equal(other.lattice_element)

    def _join(self, other: 'OctagonState') -> 'OctagonState':
        self.lattice_element.join(other.lattice_element)
        return self

    def _meet(self, other: 'OctagonState'):
        self.lattice_element.meet(other.lattice_element)
        return self

    def _widening(self, other: 'OctagonState'):
        self.lattice_element.widening(other.lattice_element)
        return self

    def replace_variable(self, variable: Identifier, pp: ProgramPoint):
        pass

    def _assign(self, left: Expression, right: Expression) -> 'State':
        raise Exception("Assignment should not be called in backward analysis.")

    def _assume(self, condition: Expression) -> 'OctagonState':
        try:
            element = _evaluator.visit(condition, self.lattice_element.copy())
            self.lattice_element.replace(element)
        # print(self)
        except NotImplementedError:
            self.top()
        return self

    def enter_if(self) -> 'OctagonState':
        return self

    def exit_if(self) -> 'OctagonState':
        return self

    def enter_loop(self) -> 'OctagonState':
        return self

    def exit_loop(self) -> 'OctagonState':
        return self

    def _output(self, output: Expression) -> 'OctagonState':
        return self

    def raise_error(self) -> 'OctagonState':
        return self.bottom()

    def _substitute(self, left: Expression, right: Expression) -> 'OctagonState':
        # try:
        variables, coefficients, constant = _evaluator.visit(right, self.lattice_element.copy().top())
        self.lattice_element.substitution(left.name, variables, coefficients, constant)
        return self
        # except NotImplementedError:
        #     self.lattice_element.project(self.indexes[left.name])
        #     return self

    def forget_variable(self, variable: VariableIdentifier, pp: int) -> 'OctagonLattice':
        dim = self.indexes[variable.name]
        print("IN FORGET", variable, dim)
        element = self.lattice_element.handle_input(dim, pp)
        # print("ELEMENT", element)
        return element

    def add_variable(self, variable: VariableIdentifier):
        pass

    def remove_variable(self, variable: VariableIdentifier):
        pass

    def copy(self):
        copy = OctagonState(self.variables)
        copy.variables_names = deepcopy(self.variables_names)
        copy.indexes = deepcopy(self.indexes)
        copy.lattice_element = self.lattice_element.copy()
        return copy

    @staticmethod
    def from_json(js):
        variable_names = dict()
        for k, v in js["variable_names"].items():
            variable_names[int(k)] = v
        lattice_element = OctagonLattice(variable_names, js["indexes"], js["dimensions"])
        if js["lincons_array"] == "T":
            return lattice_element.top()
        if js["lincons_array"] == "⊥":
            return lattice_element.bottom()
        # print("FROM JSON")
        for lincons in js["lincons_array"]:
            lattice_element.add_linear_constraint(lincons["variables"], lincons["signs"], int(lincons["constant"]), BinaryComparisonOperation.Operator.LtE)
        return lattice_element


def dict_symmetry(a: dict, b:dict):
    for k, v in a.items():
        assert k == b[v] and v == a[k], f"{a},{b}"