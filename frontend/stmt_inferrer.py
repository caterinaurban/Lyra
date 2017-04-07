"""Inferrer for python statements.

Infers the types for the following expressions:
    - Assign(expr* targets, expr value)
    - AugAssign(expr target, operator op, expr value)
    - Return(expr? value)
    - Delete(expr* targets)
    - If(expr test, stmt* body, stmt* orelse)
    - While(expr test, stmt* body, stmt* orelse)
    - For(expr target, expr iter, stmt* body, stmt* orelse)
    - AsyncFor(expr target, expr iter, stmt* body, stmt* orelse)
    - With(withitem* items, stmt* body)
    - AsyncWith(withitem* items, stmt* body)
    - Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
    - FunctionDef(identifier name, arguments args,
                       stmt* body, expr* decorator_list, expr? returns)
    - AsyncFunctionDef(identifier name, arguments args,
                             stmt* body, expr* decorator_list, expr? returns)

    TODO:
    - Import(alias* names)
    - ImportFrom(identifier? module, alias* names, int? level)
    - Global(identifier* names)
    - Nonlocal(identifier* names)
"""

import ast
import frontend.expr_inferrer as expr
import frontend.predicates as pred
import sys

from frontend.i_types import *
from frontend.constraint.constraint import *


def _infer_assignment_target(target, context, value_type):
    """Infer the type of a target in an assignment

    Attributes:
        target: the target whose type is to be inferred
        context: the current context level
        value_type: the type of the value assigned to the target

    Target cases:
        - Variable name. Ex: x = 1
        - Tuple. Ex: a, b = 1, "string"
        - List. Ex: [a, b] = [1, "string"]
        - Subscript. Ex: x[0] = 1, x[1 : 2] = [2,3], x["key"] = value
        - Compound: Ex: a, b[0], [c, d], e["key"] = 1, 2.0, [True, False], "value"

    Limitation:
        - In case of tuple/list assignments, there are no guarantees for correct number of unpacked values.
            Because the length of the list/tuple may not be resolved statically.
    TODO: Attributes assignment, UnionTypes assignment
    """
    if isinstance(target, ast.Name):
        if context.has_variable(target.id):  # Check if variable is already inferred before
            var_type = context.get_type(target.id)
            if var_type.is_subtype(value_type):
                context.set_type(target.id, value_type)
            elif not value_type.is_subtype(var_type):
                raise TypeError("The type of {} is {}. Cannot assign it to {}.".format(target.id, var_type, value_type))
        else:
            if isinstance(value_type, Generic) and not value_type.variable:
                # Happens only when the target is an iteration target
                value_type.setVariable(target.id)
            context.set_type(target.id, value_type)

    elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):  # Tuple/List assignment
        if not pred.is_sequence(value_type):
            raise ValueError("Cannot unpack a non sequence.")
        for i in range(len(target.elts)):
            seq_elem = target.elts[i]
            if isinstance(value_type, TString):
                _infer_assignment_target(seq_elem, context, value_type)
            elif isinstance(value_type, TList):
                _infer_assignment_target(seq_elem, context, value_type.type)
            elif isinstance(value_type, TTuple):
                _infer_assignment_target(seq_elem, context, value_type.types[i])
    elif isinstance(target, ast.Subscript):  # Subscript assignment
        expr.infer(target, context)
        indexed_type = expr.infer(target.value, context)
        if isinstance(indexed_type, TString):
            raise TypeError("String objects don't support item assignment.")
        elif isinstance(indexed_type, TTuple):
            raise TypeError("Tuple objects don't support item assignment.")
        elif isinstance(indexed_type, TList):
            if isinstance(target.slice, ast.Index):
                if indexed_type.type.is_subtype(value_type):  # Update the type of the list with the more generic type
                    if isinstance(target.value, ast.Name):
                        context.set_type(target.value.id, TList(value_type))
                elif not value_type.is_subtype(indexed_type.type):
                    raise TypeError("Cannot assign {} to {}.".format(value_type, indexed_type.type))
            else:  # Slice subscription
                if indexed_type.is_subtype(value_type):
                    if isinstance(target.value, ast.Name):  # Update the type of the list with the more generic type
                        context.set_type(target.value.id, value_type)
                elif not (isinstance(value_type, TList) and value_type.type.is_subtype(indexed_type.type)):
                    raise TypeError("Cannot assign {} to {}.".format(value_type, indexed_type))
        elif isinstance(indexed_type, TDictionary):
            if indexed_type.value_type.is_subtype(value_type):
                if isinstance(target.value,
                              ast.Name):  # Update the type of the dictionary values with the more generic type
                    context.get_type(target.value.id).value_type = value_type
            elif not value_type.is_subtype(indexed_type.value_type):
                raise TypeError(
                    "Cannot assign {} to a dictionary item of type {}.".format(value_type, indexed_type.value_type))
        else:
            raise NotImplementedError("The inference for {} subscripting is not supported.".format(indexed_type))
    else:
        raise NotImplementedError("The inference for {} assignment is not supported.".format(type(target).__name__))


def _infer_assign(node, context, constraint_problem):
    """Infer the types of target variables in an assignment node."""
    # The type of the value assigned to the targets in the assignment statement.
    value_type = expr.infer(node.value, context, constraint_problem)
    for target in node.targets:
        _infer_assignment_target(target, context, value_type)

    return TNone()


def _infer_augmented_assign(node, context, constraint_problem):
    """Infer the types for augmented assignments

    Examples:
        a += 5
        b[2] &= x

    TODO: Attribute augmented assignment
    """
    target_type = expr.infer(node.target, context, constraint_problem)
    value_type = expr.infer(node.value, context, constraint_problem)
    result_type = expr.binary_operation_type(target_type, node.op, value_type, constraint_problem)
    if isinstance(node.target, ast.Name):
        # If result_type was a supertype of target_type, replace it in the context
        context.set_type(node.target.id, result_type)
    elif isinstance(node.target, ast.Subscript):
        indexed_type = expr.infer(node.target.value, context, constraint_problem)
        if isinstance(indexed_type, TString):
            raise TypeError("String objects don't support item assignment.")
        elif isinstance(indexed_type, TTuple):
            raise TypeError("Tuple objects don't support item assignment.")
        elif isinstance(indexed_type, TDictionary):
            if not isinstance(result_type, type(indexed_type.value_type)):
                raise TypeError("Cannot convert the dictionary value from {} to {}.".format(indexed_type.value_type,
                                                                                            result_type))
        elif isinstance(indexed_type, TList):
            if not isinstance(result_type, type(indexed_type.type)):
                raise TypeError("Cannot convert the list values from {} to {}.".format(indexed_type.type,
                                                                                       result_type))
        else:
            # This block should never be executed.
            raise TypeError("Unknown subscript type.")
    elif isinstance(node.target, ast.Attribute):
        # TODO: Implement after classes inference
        pass
    return TNone()


def _delete_element(target, context, constraint_problem):
    """Remove (if needed) a target from the context

    Cases:
        - del var_name: remove its type mapping from the context directly.
        - del subscript:
                    * Tuple/String --> Immutable. Raise exception.
                    * List/Dict --> Do nothing to the context.
    TODO: Attribute deletion
    """
    if isinstance(target, (ast.Tuple, ast.List)):  # Multiple deletions
        for elem in target.elts:
            _delete_element(elem, context, constraint_problem)
    elif isinstance(target, ast.Name):
        context.delete_type(target.id)
    elif isinstance(target, ast.Subscript):
        indexed_type = expr.infer(target.value, context, constraint_problem)
        if isinstance(indexed_type, TString):
            raise TypeError("String objects don't support item deletion.")
        elif isinstance(indexed_type, TTuple):
            raise TypeError("Tuple objects don't support item deletion.")


def _infer_delete(node, context, constraint_problem):
    """Remove (if needed) the type of the deleted items in the current context"""
    for target in node.targets:
        _delete_element(target, context, constraint_problem)

    return TNone()


def _infer_body(body, context, constraints_problem):
    """Infer the type of a code block containing multiple statements"""
    body_type = TNone()
    for stmt in body:
        stmt_type = infer(stmt, context, constraints_problem)
        if body_type.is_subtype(stmt_type) or isinstance(body_type, TNone):
            body_type = stmt_type
        elif not (stmt_type.is_subtype(body_type) or isinstance(stmt_type, TNone)):
            if isinstance(body_type, UnionTypes):
                body_type.union(stmt_type)
            elif isinstance(stmt_type, UnionTypes):
                stmt_type.union(body_type)
                body_type = stmt_type
            else:
                union = {body_type, stmt_type}
                body_type = UnionTypes(union)
    return body_type


def _infer_control_flow(node, context, constraint_problem):
    """Infer the type(s) for an if/while/for statements block.

    Arguments:
        node: The AST node to be inferred
        context: the current context level
    Example:
        if (some_condition):
            ......
            return "some string"
        else:
            ......
            return 2.0

        type: Union{String, Float}
    """
    body_type = _infer_body(node.body, context, constraint_problem)
    else_type = _infer_body(node.orelse, context, constraint_problem)

    if body_type.is_subtype(else_type):
        return else_type
    elif else_type.is_subtype(body_type):
        return body_type

    if isinstance(body_type, UnionTypes):
        body_type.union(else_type)
        return body_type
    elif isinstance(else_type, UnionTypes):
        else_type.union(body_type)
        return else_type
    return UnionTypes({body_type, else_type})


def _infer_for(node, context, constraint_problem):
    """Infer the type for a for loop node

    Limitation:
        - The iterable can't be a tuple.
            For example: the following is not allowed:
                for x in (1, 2.0, "string"):
                    ....
    """
    iter_type = expr.infer(node.iter, context, constraint_problem)
    value_type = iter_type
    if isinstance(iter_type, Generic):
        value_type = key_type = Generic([Type()], constraint_problem=constraint_problem)
        iter_type.narrow([TSequence(), TDictionary(t_k=key_type), TSet(t=key_type)])
    elif not isinstance(iter_type, (TList, TSet, TIterator, TBytesString, TDictionary, TString)):
        raise TypeError("{} is not iterable.".format(iter_type))

    # Infer the target in the loop, inside the global context
    # Cases:
    # - Var name. Ex: for i in range(5)..
    # - Tuple. Ex: for (a,b) in [(1,"st"), (3,"st2")]..
    # - List. Ex: for [a,b] in [(1, "st"), (3, "st2")]..
    if isinstance(iter_type, (TList, TSet, TIterator)):
        value_type = value_type.type
    elif isinstance(iter_type, TDictionary):
        value_type = value_type.key_type

    _infer_assignment_target(node.target, context, value_type)

    return _infer_control_flow(node, context, constraint_problem)


def _infer_with(node, context, constraint_problem):
    """Infer the types for a with block"""
    for item in node.items:
        if item.optional_vars:
            item_type = expr.infer(item.context_expr, context, constraint_problem)
            _infer_assignment_target(item.optional_vars, context, item_type)

    return _infer_body(node.body, context, constraint_problem)


def _infer_try(node, context, constraint_problem):
    """Infer the types for a try/except/else block"""
    try_type = UnionTypes()

    try_type.union(_infer_body(node.body, context, constraint_problem))
    try_type.union(_infer_body(node.orelse, context, constraint_problem))
    try_type.union(_infer_body(node.finalbody, context, constraint_problem))
    # TODO: Infer exception handlers as classes

    for handler in node.handlers:
        try_type.union(_infer_body(handler.body, context, constraint_problem))

    if len(try_type.types) == 1:
        return list(try_type.types)[0]
    return try_type


def init_func_def(args, context):
    """Initialize the local context of the function and the constraints problem for the args domains."""
    # TODO handle starred args
    function_context = Context(parent_context=context)
    constraints_problem = Problem()

    for arg in args:
        # TODO use annotation if possible
        domain = Generic([Type()], arg.arg, constraints_problem)
        function_context.set_type(arg.arg, domain)
        constraints_problem.addVariable(arg.arg, domain)

    return function_context, constraints_problem


def _narrow_with_constraints(t, solutions):
    """Narrow a Generic type t based on values appearing in the constraints problem solutions"""
    if not isinstance(t, Generic):
        return
    possible = []
    for sol in solutions:
        possible.append(sol[t.variable])
    t.narrow(possible)


def infer_func_def(node, context):
    function_context, constraint_problem = init_func_def(node.args.args, context)
    return_type = _infer_body(node.body, function_context, constraint_problem)

    args_types = []
    for arg in node.args.args:
        args_types.append(function_context.get_type(arg.arg))

    constraints_sols = constraint_problem.getSolutions()

    _narrow_with_constraints(return_type, constraints_sols)
    for arg_t in args_types:
        _narrow_with_constraints(arg_t, constraints_sols)
    function_type = TFunction(return_type, args_types, constraints_sols)
    context.set_type(node.name, function_type)
    return TNone()


def infer(node, context, constraint_problem=None):
    if isinstance(node, ast.Assign):
        return _infer_assign(node, context, constraint_problem)
    elif isinstance(node, ast.AugAssign):
        return _infer_augmented_assign(node, context, constraint_problem)
    elif isinstance(node, ast.Return):
        return expr.infer(node.value, context, constraint_problem)
    elif isinstance(node, ast.Delete):
        return _infer_delete(node, context, constraint_problem)
    elif isinstance(node, (ast.If, ast.While)):
        return _infer_control_flow(node, context, constraint_problem)
    elif isinstance(node, ast.For):
        return _infer_for(node, context, constraint_problem)
    elif sys.version_info[0] >= 3 and sys.version_info[1] >= 5 and isinstance(node, ast.AsyncFor):
        # AsyncFor is introduced in Python 3.5
        return _infer_for(node, context, constraint_problem)
    elif isinstance(node, ast.With):
        return _infer_with(node, context, constraint_problem)
    elif sys.version_info[0] >= 3 and sys.version_info[1] >= 5 and isinstance(node, ast.AsyncWith):
        # AsyncWith is introduced in Python 3.5
        return _infer_with(node, context, constraint_problem)
    elif isinstance(node, ast.Try):
        return _infer_try(node, context, constraint_problem)
    elif isinstance(node, ast.FunctionDef):
        return infer_func_def(node, context)
    elif sys.version_info[0] >= 3 and sys.version_info[1] >= 5 and isinstance(node, ast.AsyncFunctionDef):
        # AsyncWith is introduced in Python 3.5
        return infer_func_def(node, context)
    return TNone()
