import ast
import optparse
import sys

from lyra.core.cfg import *
from lyra.core.expressions import Literal
from lyra.core.statements import *
from lyra.core.types import IntegerLyraType, BooleanLyraType, resolve_type_annotation, \
    FloatLyraType, ListLyraType, TupleLyraType, StringLyraType, DictLyraType, SetLyraType
from lyra.visualization.graph_renderer import CFGRenderer


class LooseControlFlowGraph:
    class SpecialEdgeType(Enum):
        BREAK = 1
        CONTINUE = 2

    def __init__(self, nodes: Set[Node] = None, in_node: Node = None, out_node: Node = None,
                 edges: Set[Edge] = None,
                 loose_in_edges=None, loose_out_edges=None, both_loose_edges=None):
        """Loose control flow graph representation.

        This representation uses a complete (non-loose) control flow graph via aggregation
        and adds loose edges and
        some transformations methods to combine, prepend and append loose control flow graphs.
        This class
        intentionally does not provide access to the linked CFG.
        The completed CFG can be retrieved finally with
        `eject()`.

        :param nodes: optional set of nodes of the control flow graph
        :param in_node: optional entry node of the control flow graph
        :param out_node: optional exit node of the control flow graph
        :param edges: optional set of edges of the control flow graph
        :param loose_in_edges: optional set of loose edges
        that have no start yet and end inside this CFG
        :param loose_out_edges: optional set of loose edges
        that start inside this CFG and have no end yet
        :param both_loose_edges: optional set of loose edges, loose on both ends
        """
        assert not in_node or not (loose_in_edges or both_loose_edges)
        assert not out_node or not (loose_out_edges or both_loose_edges)
        assert all([e.source is None for e in loose_in_edges or []])
        assert all([e.target is None for e in loose_out_edges or []])
        assert all([e.source is None and e.target is None for e in both_loose_edges or []])

        self._cfg = ControlFlowGraph(nodes or set(), in_node, out_node, edges or set())
        self._loose_in_edges = loose_in_edges or set()
        self._loose_out_edges = loose_out_edges or set()
        self._both_loose_edges = both_loose_edges or set()
        self._special_edges = []

    @property
    def nodes(self) -> Dict[int, Node]:
        return self._cfg.nodes

    @property
    def in_node(self) -> Node:
        return self._cfg.in_node

    @in_node.setter
    def in_node(self, node):
        self._cfg._in_node = node

    @property
    def out_node(self) -> Node:
        return self._cfg.out_node

    @out_node.setter
    def out_node(self, node):
        self._cfg._out_node = node

    @property
    def edges(self) -> Dict[Tuple[Node, Node], Edge]:
        return self._cfg.edges

    @property
    def loose_in_edges(self) -> Set[Edge]:
        return self._loose_in_edges

    @property
    def loose_out_edges(self) -> Set[Edge]:
        return self._loose_out_edges

    @property
    def both_loose_edges(self) -> Set[Edge]:
        return self._both_loose_edges

    @property
    def special_edges(self) -> List[Tuple[Edge, SpecialEdgeType]]:
        return self._special_edges

    @property
    def cfgs(self):
        return self._cfgs

    def loose(self):
        loose = len(self.loose_in_edges) or len(self.loose_out_edges) or len(self.both_loose_edges)
        return loose or len(self.special_edges)

    def add_node(self, node):
        self.nodes[node.identifier] = node

    def add_edge(self, edge):
        """Add a (loose/normal) edge to this loose CFG.
        """
        if not edge.source and not edge.target:
            self.both_loose_edges.add(edge)
            self._cfg._in_node = None
            self._cfg._out_node = None
        elif not edge.source:
            self.loose_in_edges.add(edge)
            self._cfg._in_node = None
        elif not edge.target:
            self.loose_out_edges.add(edge)
            self._cfg._out_node = None
        else:
            self.edges[edge.source, edge.target] = edge

    def remove_edge(self, edge):
        del self.edges[(edge.source, edge.target)]

    def remove_node(self, node):
        """Remove a node and all its out edges from the CFG.
        """
        edges_to_be_removed = self.get_edges_with_source(node)
        del self.nodes[node.identifier]

        nodes_to_be_removed = []
        for edge_to_be_removed in edges_to_be_removed:
            target = edge_to_be_removed.target
            self.remove_edge(edge_to_be_removed)
            if target is not self.out_node and len(self.get_edges_with_target(target)) == 0:
                nodes_to_be_removed.append(target)
        for node_to_be_removed in nodes_to_be_removed:
            self.remove_node(node_to_be_removed)




    def get_edges_with_source(self, source):
        return [edge for edge in self.edges.values() if edge.source is source]

    def get_edges_with_target(self, target):
        return [edge for edge in self.edges.values() if edge.target is target]

    def combine(self, other):
        assert not (self.in_node and other.in_node)
        assert not (self.out_node and other.out_node)
        self.nodes.update(other.nodes)
        self.edges.update(other.edges)
        self.loose_in_edges.update(other.loose_in_edges)
        self.loose_out_edges.update(other.loose_out_edges)
        self.both_loose_edges.update(other.both_loose_edges)
        self.special_edges.extend(other.special_edges)
        self._cfg._in_node = other.in_node or self.in_node  # agree on in_node
        self._cfg._out_node = other.out_node or self.out_node  # agree on out_node
        return self

    def prepend(self, other):
        other.append(self)
        self.replace(other)

    def append(self, other):
        assert not (self.loose_out_edges and other.loose_in_edges)
        assert not self.both_loose_edges or (
                not other.loose_in_edges and not other.both_loose_edges)

        self.nodes.update(other.nodes)
        self.edges.update(other.edges)

        edge_added = False
        if self.loose_out_edges:
            edge_added = True
            for e in self.loose_out_edges:
                e._target = other.in_node
                # updated/created edge is not yet in edge dict -> add
                self.edges[(e.source, e.target)] = e
            # clear loose edge sets
            self._loose_out_edges = set()
        elif other.loose_in_edges:
            edge_added = True
            for e in other.loose_in_edges:
                e._source = self.out_node
                # updated/created edge is not yet in edge dict -> add
                self.edges[(e.source, e.target)] = e
            # clear loose edge set
            other._loose_in_edges = set()

        if self.both_loose_edges:
            edge_added = True
            for e in self.both_loose_edges:
                e._target = other.in_node
                self.add_edge(e)  # updated/created edge is not yet in edge dict -> add
            # clear loose edge set
            self._both_loose_edges = set()
        elif other.both_loose_edges:
            edge_added = True
            for e in other.both_loose_edges:
                e._source = self.out_node
                self.add_edge(e)  # updated/created edge is not yet in edge dict -> add
            # clear loose edge set
            other._both_loose_edges = set()
        if not edge_added:
            # neither of the CFGs has loose ends -> add unconditional edge
            e = Unconditional(self.out_node, other.in_node)
            # updated/created edge is not yet in edge dict -> add
            self.edges[(e.source, e.target)] = e

        # in any case, transfer loose_out_edges of other to self
        self.loose_out_edges.update(other.loose_out_edges)
        self.special_edges.extend(other.special_edges)
        self._cfg._out_node = other.out_node

        return self

    def eject(self) -> ControlFlowGraph:
        if self.loose():
            error = 'This control flow graph is still loose'
            error += ' and cannot eject a complete control flow graph!'
            raise TypeError(error)
        return self._cfg

    def replace(self, other):
        self.__dict__.update(other.__dict__)


def _dummy_node(id_gen):
    return Basic(id_gen.next)


def _dummy_cfg(id_gen):
    dummy = _dummy_node(id_gen)
    return LooseControlFlowGraph({dummy}, dummy, dummy, set())


class CFGFactory:
    """
    A helper class that encapsulates a partial CFG
    and possibly some statements not yet attached to the CFG.

    Whenever the
    method `complete_basic_block()` is called,
    it is ensured that all unattached statements are properly attached to the
    partial CFG. The partial CFG can be retrieved at any time by property `cfg`.
    """

    def __init__(self, id_gen):
        self._stmts = []
        self._cfg = None
        self._id_gen = id_gen

    @property
    def cfg(self):
        return self._cfg

    def prepend_cfg(self, other):
        if self._cfg is not None:
            self._cfg.prepend(other)
        else:
            self._cfg = other
        return self._cfg

    def append_cfg(self, other):
        if self._cfg is not None:
            if self._cfg.loose_out_edges and other.loose_in_edges:
                self._cfg.append(_dummy_cfg(self._id_gen))
            self._cfg.append(other)
        else:
            self._cfg = other
        return self._cfg

    def add_stmts(self, stmts):
        """
        Adds statements to the currently open block.
        :param stmts: a single statement or an iterable of statements
        :return:
        """
        if isinstance(stmts, List):
            self._stmts.extend(stmts)
        else:
            self._stmts.append(stmts)

    def complete_basic_block(self):
        if self._stmts:
            block = Basic(self._id_gen.next, self._stmts)
            self.append_cfg(LooseControlFlowGraph({block}, block, block, set()))
            self._stmts = []

    def incomplete_block(self):
        return len(self._stmts) > 0


# noinspection PyPep8Naming
class CFGVisitor(ast.NodeVisitor):
    """AST visitor that generates a CFG for each function."""

    class NodeIdentifierGenerator:
        """Helper class that generates an increasing sequence of node identifiers."""

        def __init__(self):
            self._next = 0

        @property
        def next(self):
            self._next += 1
            return self._next

    def __init__(self):
        super().__init__()
        self._id_gen = CFGVisitor.NodeIdentifierGenerator()
        self._cfgs = {}
        self._function_defs = {}

    def visit(self, node, *args, **kwargs):
        """Visit an AST node.

        :param node: node to be visited
        :return: either a statement or a partial CFG, depending on the visited node

        :keyword arguments:
            * *types* -- dictionary mapping (variable) names to their corresponding (lyra) type
            * *typ* -- type of the current node
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        print(type(node).__name__)
        raise NotImplementedError(f"Visit of {node.__class__.__name__} is unsupported!")

    # Literals

    # noinspection PyUnusedLocal
    def visit_Num(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a number (integer, float, or complex).
        The n attribute stores the value, already converted to the relevant type."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.n, int):
            expr = Literal(IntegerLyraType(), str(node.n))
            return LiteralEvaluation(pp, expr)
        elif isinstance(node.n, float):
            expr = Literal(FloatLyraType(), str(node.n))
            return LiteralEvaluation(pp, expr)
        raise NotImplementedError(f"Num of type {node.n.__class__.__name__} is unsupported!")

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def visit_Str(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a string. The s attribute stores the value."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        expr = Literal(StringLyraType(), node.s)
        return LiteralEvaluation(pp, expr)

    def visit_List(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a list.
        The elts attribute stores a list of nodes representing the elements.
        The ctx attribute is Store if the container is an assignment target, and Load otherwise."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, ListLyraType):
            items = [self.visit(item, types, typ.typ, function_name=function_name) for item in node.elts]
        else:
            items = [self.visit(item, types, None, function_name=function_name) for item in node.elts]
        return ListDisplayAccess(pp, typ, items)

    def visit_Tuple(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a tuple.
        The elts attribute stores a list of nodes representing the elements.
        The ctx attribute is Store if the container is an assignment target, and Load otherwise."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, TupleLyraType):
            items = [self.visit(item, types, i_typ, function_name=function_name)
                     for item, i_typ in zip(node.elts, typ.typs)]
        else:
            items = [self.visit(item, types, None, function_name=function_name) for item in node.elts]
        return TupleDisplayAccess(pp, typ, items)

    def visit_Set(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a set.
        The elts attribute stores a list of nodes representing the elements."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, SetLyraType):
            items = [self.visit(item, types, typ.typ, function_name=function_name) for item in node.elts]
        else:
            items = [self.visit(item, types, None, function_name=function_name) for item in node.elts]
        return SetDisplayAccess(pp, typ, items)

    def visit_Dict(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a dictionary.
        The attributes keys and values store lists of nodes with matching order
        representing the keys and the values, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, DictLyraType):
            keys = [self.visit(key, types, typ.key_typ, function_name=function_name) for key in node.keys]
            values = [self.visit(value, types, typ.val_typ, function_name=function_name) for value in node.values]
        else:
            keys = [self.visit(key, types, None, function_name=function_name) for key in node.keys]
            values = [self.visit(value, types, None, function_name=function_name) for value in node.values]
        return DictDisplayAccess(pp, typ, keys, values)

    # noinspection PyUnusedLocal
    def visit_NameConstant(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for True, False or None.
        The value attribute stores the constant."""
        if isinstance(node.value, bool):
            pp = ProgramPoint(node.lineno, node.col_offset)
            expr = Literal(BooleanLyraType(), str(node.value))
            return LiteralEvaluation(pp, expr)
        raise NotImplementedError(f"Constant {node.value.__class__.__name__} is unsupported!")

    # Variables

    def visit_Name(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a variable name.
        The attribute id stores the name as a string.
        The attribute ctx is Store (to assign a new value to the variable),
        Load (to load the value of the variable), or Del (to delete the variable)."""

        node.id = function_name + "#" + node.id if function_name is not 'main' else node.id

        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.ctx, ast.Store):
            if node.id not in types:
                if typ:
                    types[node.id] = typ
                else:
                    raise ValueError(f"Missing type annotation for variable {node.id}!")
            expr = VariableIdentifier(types[node.id], node.id)
            return VariableAccess(pp, types[node.id], expr)
        if isinstance(node.ctx, ast.Load):
            assert node.id in types
            # assert types[node.id] == typ or typ is None
            expr = VariableIdentifier(types[node.id], node.id)
            return VariableAccess(pp, types[node.id], expr)
        assert isinstance(node.ctx, ast.Del)
        raise NotImplementedError(f"Name deletion is unsupported!")

    # Expressions

    # noinspection PyUnusedLocal
    def visit_Expr(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for an expression statement (whose return value is unused).
        The attribute value stored another AST node."""
        return self.visit(node.value, types, function_name=function_name)

    def visit_UnaryOp(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a unary operation.
        The attributes op and operand store the operator
        and any expression node, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        name = type(node.op).__name__.lower()
        argument = self.visit(node.operand, types, typ, function_name=function_name)
        return Call(pp, name, [argument], typ)

    def visit_BinOp(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a binary operation.
        The attributes op, left, and right store the operator
        and any expression nodes, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        name = type(node.op).__name__.lower()
        left = self.visit(node.left, types, typ, function_name=function_name)
        right = self.visit(node.right, types, typ, function_name=function_name)
        return Call(pp, name, [left, right], typ)

    def visit_BoolOp(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a boolean operation.
        The attributes op and values store the operand
        and a list of any expression node representing the operand involved, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        name = type(node.op).__name__.lower()
        arguments = [self.visit(val, types, typ, function_name=function_name) for val in node.values]
        return Call(pp, name, arguments, typ)

    def visit_Compare(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a comparison operation.
        The attributes left, ops, and comparators store the first value in the comparison,
        the list of operators, and the list of compared values after the first."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert isinstance(typ, BooleanLyraType)  # we expect typ to be a BooleanLyraType
        left = self.visit(node.left, types, None, function_name=function_name)
        name = type(node.ops[0]).__name__.lower()
        second = self.visit(node.comparators[0], types, None, function_name=function_name)
        result = Call(pp, name, [left, second], typ)
        for op, comparator in zip(node.ops[1:], node.comparators[1:]):
            name = type(op).__name__.lower()
            right = self.visit(comparator, types, None, function_name=function_name)
            current = Call(pp, name, [second, right], typ)
            result = Call(pp, 'and', [result, current], typ)
            second = right
        return result

    def visit_Call(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a call.
        The attribute func stores the function being called (often a Name or Attribute object).
        The attribute args stores a list fo the arguments passed by position."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.func, ast.Name):
            name: str = node.func.id
            if name == 'bool' or name == 'int' or name == 'str':
                arguments = [self.visit(arg, types, typ, function_name=function_name) for arg in node.args]
                return Call(pp, name, arguments, typ)
            if name == 'input':
                arguments = [self.visit(arg, types, StringLyraType(), function_name=function_name) for arg in node.args]
                return Call(pp, name, arguments, StringLyraType())
            if name == 'range':
                arguments = [self.visit(arg, types, IntegerLyraType(), function_name=function_name)
                             for arg in node.args]
                return Call(pp, name, arguments, ListLyraType(IntegerLyraType()))
            arguments = [self.visit(arg, types, None, function_name=function_name) for arg in node.args]
            return Call(pp, name, arguments, typ)
        elif isinstance(node.func, ast.Attribute):
            name: str = node.func.attr
            if name == 'append':
                arguments = [self.visit(node.func.value, types, None, function_name=function_name)] # target of the call
                args = [self.visit(arg, types, None, function_name=function_name) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, ListLyraType)
                return Call(pp, name, arguments, arguments[0].typ)
            if name == 'items':
                arguments = [self.visit(node.func.value, types, None, function_name=function_name)] # target of the call
                args = [self.visit(arg, types, None, function_name=function_name) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, DictLyraType)
                tuple_typ = TupleLyraType([arguments[0].typ.key_typ, arguments[0].typ.val_typ])
                return Call(pp, name, arguments, SetLyraType(tuple_typ))
            if name == 'keys':
                arguments = [self.visit(node.func.value, types, None, function_name=function_name)] # target of the call
                args = [self.visit(arg, types, None, function_name=function_name) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, DictLyraType)
                return Call(pp, name, arguments, SetLyraType(arguments[0].typ.key_typ))
            if name == 'rstrip' or name == 'strip':
                arguments = [self.visit(node.func.value, types, None, function_name=function_name)] # target of the call
                args = [self.visit(arg, types, None, function_name=function_name) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, StringLyraType)
                return Call(pp, name, arguments, arguments[0].typ)
            if name == 'split':  # str.split([sep[, maxsplit]])
                assert isinstance(typ, ListLyraType)  # we expect type to be a ListLyraType
                arguments = [self.visit(node.func.value, types, typ.typ, function_name=function_name)]
                # target of the call
                args_typs = zip(node.args, [typ.typ, IntegerLyraType()])
                args = [self.visit(arg, types, arg_typ, function_name=function_name) for arg, arg_typ in args_typs]
                arguments.extend(args)
                return Call(pp, name, arguments, typ)
            if name == 'values':
                arguments = [self.visit(node.func.value, types, None, function_name=function_name)] # target of the call
                args = [self.visit(arg, types, None, function_name=function_name) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, DictLyraType)
                return Call(pp, name, arguments, SetLyraType(arguments[0].typ.val_typ))
            arguments = [self.visit(node.func.value, types, None, function_name=function_name)]  # target of the call
            arguments.extend([self.visit(arg, types, None, function_name=function_name) for arg in node.args])
            return Call(pp, name, arguments, typ)

    def visit_IfExp(self, node, targets, op=None, types=None, typ=None, function_name='main'):
        """Visitor function for an if expression.
        The components of the expression are stored in the attributes test, body, and orelse."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        then = CFGFactory(self._id_gen)
        body = self.visit(node.body, types, typ, function_name=function_name)
        assignments = list()
        for target in targets:
            if op:
                left = self.visit(target, types, typ)
                name = type(op).__name__.lower()
                value = Call(pp, name, [left, body], left.typ)
                assignments.append(Assignment(pp, left, value))
            else:
                assignments.append(Assignment(pp, self.visit(target, types, typ, function_name=function_name), body))
        then.add_stmts(assignments)
        then.complete_basic_block()
        then = then.cfg[function_name]
        test = self.visit(node.test, types, BooleanLyraType(), function_name=function_name)
        then.add_edge(Conditional(None, test, then.in_node, Edge.Kind.IF_IN))
        then.add_edge(Unconditional(then.out_node, None, Edge.Kind.IF_OUT))
        orelse = CFGFactory(self._id_gen)
        body = self.visit(node.orelse, types, typ, function_name=function_name)
        assignments = list()
        for target in targets:
            if op:
                left = self.visit(target, types, typ, function_name=function_name)
                name = type(op).__name__.lower()
                value = Call(pp, name, [left, body], left.typ)
                assignments.append(Assignment(pp, left, value))
            else:
                assignments.append(Assignment(pp, self.visit(target, types, typ), body))
        orelse.add_stmts(assignments)
        orelse.complete_basic_block()
        orelse = orelse.cfg[function_name]
        not_test = Call(pp, 'not', [test], BooleanLyraType())
        orelse.add_edge(Conditional(None, not_test, orelse.in_node, Edge.Kind.IF_IN))
        orelse.add_edge(Unconditional(orelse.out_node, None, Edge.Kind.IF_OUT))
        return then.combine(orelse)

    # Subscripting

    def visit_Subscript(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a subscript.
        The attribute value stores the target of the subscript (often a Name).
        The attribute slice is one of Index, Slice, or ExtSlice.
        The attribute ctx is Load, Store, or Del."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.slice, ast.Index):
            target = self.visit(node.value, types, None, function_name=function_name)
            key = self.visit(node.slice.value, types, None, function_name=function_name)
            return SubscriptionAccess(pp, typ, target, key)
        elif isinstance(node.slice, ast.Slice):
            value = self.visit(node.value, types, None, function_name=function_name)
            lower = self.visit(node.slice.lower, types, None, function_name=function_name)
            upper = self.visit(node.slice.upper, types, None, function_name=function_name) if node.slice.upper else None
            step = self.visit(node.slice.step, types, None, function_name=function_name) if node.slice.step else None
            return SlicingAccess(pp, typ, value, lower, upper, step)
        raise NotImplementedError(f"Subscription {node.slice.__class__.__name__} is unsupported!")

    # Statements

    def visit_Assign(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for an assignment.
        The attribute targets stores a list of targets of the assignment.
        The attribute value stores the assigned value."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert typ is None  # we expect typ to be None
        assignments = list()
        assert len(node.targets) == 1
        target = self.visit(node.targets[0], types, None, function_name=function_name)
        value = self.visit(node.value, types, target.typ, function_name=function_name)
        return Assignment(pp, target, value)

    def visit_AnnAssign(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for an assignment with a type annotation.
        The attribute target stores the target of the assignment (a Name, Attribute, or Subscript).
        The attribute annotation stores the type annotation (a Str or Name).
        The attribute value optionally stores the assigned value."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert typ is None  # we expect typ to be None
        annotated = resolve_type_annotation(node.annotation)
        target = self.visit(node.target, types, annotated, function_name=function_name)
        value = self.visit(node.value, types, annotated, function_name=function_name)
        return Assignment(pp, target, value)

    def visit_AugAssign(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for an augmented assignment.
        The attribute target stores the target of the assignment (a Name, Attribute, or Subscript).
        The attributes op and value store the operation and the assigned value, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert typ is None  # we expect typ to be None
        target = self.visit(node.target, types, None, function_name=function_name)
        name = type(node.op).__name__.lower()
        right = self.visit(node.value, types, None, function_name=function_name)
        value = Call(pp, name, [target, right], target.typ)
        return Assignment(pp, target, value)

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def visit_Raise(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for an exception raise.
        The attribute exc stores the exception object to be raised
        (normally a Call or Name, or None for a standalone raise)."""
        return Raise(ProgramPoint(node.lineno, node.col_offset))

    # Control Flow

    def visit_If(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for an if statement.
        The attribute test stores a single AST node.
        The attributes body and orelse each store a list of AST nodes to be executed."""
        pp = ProgramPoint(node.test.lineno, node.test.col_offset)

        body = self._visit_body(node.body, types, typ, function_name=function_name)
        test = self.visit(node.test, types, BooleanLyraType(), function_name=function_name)
        body.add_edge(Conditional(None, test, body.in_node, Edge.Kind.IF_IN))
        if body.out_node:  # control flow can exit the body
            # add an unconditional IF_OUT edge
            body.add_edge(Unconditional(body.out_node, None, Edge.Kind.IF_OUT))

        if node.orelse:  # there is an else branch
            orelse = self._visit_body(node.orelse, types, typ, function_name=function_name)
            not_test = Call(pp, 'not', [test], BooleanLyraType())
            orelse.add_edge(Conditional(None, not_test, orelse.in_node, Edge.Kind.IF_IN))
            if orelse.out_node:  # control flow can exit the else
                # add an unconditional IF_OUT edge
                orelse.add_edge(Unconditional(orelse.out_node, None, Edge.Kind.IF_OUT))

            # handle special edges
            for special, _ in orelse.special_edges:
                # create dummy node
                dummy = _dummy_node(self._id_gen)
                orelse.add_node(dummy)
                # add an unconditional IF_OUT edge to the newly created dummy node
                orelse.add_edge(Unconditional(special.source, dummy, Edge.Kind.IF_OUT))
                # move the special edge after the dummy node
                special._source = dummy

        else:  # there is no else branch
            orelse = LooseControlFlowGraph()
            not_test = Call(pp, 'not', [test], BooleanLyraType())
            orelse.add_edge(Conditional(None, not_test, None, Edge.Kind.DEFAULT))

        # handle special edges
        for special, edge_type in body.special_edges:
            # create dummy node
            dummy = _dummy_node(self._id_gen)
            body.add_node(dummy)
            # add an unconditional IF_OUT edge to the newly created dummy node
            body.add_edge(Unconditional(special.source, dummy, Edge.Kind.IF_OUT))
            # move the special edge after the dummy node
            special._source = dummy

        cfg = body.combine(orelse)
        return cfg

    def visit_While(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for an while statement.
        The attribute test stores a single AST node.
        The attributes body and orelse each store a list of AST nodes to be executed."""
        pp = ProgramPoint(node.test.lineno, node.test.col_offset)

        body = self._visit_body(node.body, types, typ, function_name=function_name)
        test = self.visit(node.test, types, BooleanLyraType(), function_name=function_name)
        header = Loop(self._id_gen.next)
        body_in_node = body.in_node
        body_out_node = body.out_node
        body.add_node(header)
        body.in_node = header
        body.add_edge(Conditional(header, test, body_in_node, Edge.Kind.LOOP_IN))
        not_test = Call(pp, 'not', [test], BooleanLyraType())
        body.add_edge(Conditional(header, not_test, None))
        if body_out_node:  # control flow can exit the body
            # add an unconditional LOOP_OUT edge
            body.add_edge(Unconditional(body_out_node, header, Edge.Kind.LOOP_OUT))

        if node.orelse:  # there is an else branch
            orelse = self._visit_body(node.orelse, types, function_name=function_name)
            if orelse.out_node:  # control flow can exit the else
                # add an unconditional DEFAULT edge
                orelse.add_edge(Unconditional(orelse.out_node, None, Edge.Kind.DEFAULT))
            body.append(orelse)

        # handle special edges
        for special, kind in body.special_edges:
            if kind == LooseControlFlowGraph.SpecialEdgeType.CONTINUE:
                body.add_edge(Unconditional(special.source, header, Edge.Kind.LOOP_OUT))
            elif kind == LooseControlFlowGraph.SpecialEdgeType.BREAK:
                body.add_edge(Unconditional(special.source, None, Edge.Kind.LOOP_OUT))
        body.special_edges.clear()

        return body

    def visit_For(self, node, types=None, typ=None, function_name='main'):
        """Visitor function for a for statement.
        The attribute target stores the variable(s) the loop assigns to
        (as a single Name, Tuple, or List node).
        The attribute iter stores a single AST node representing the item to be looped over.
        The attributes body and orelse each store a list of AST nodes to be executed."""
        pp = ProgramPoint(node.target.lineno, node.target.col_offset)

        iterated = self.visit(node.iter, types, None, function_name=function_name)
        target_typ = None
        if isinstance(iterated, VariableAccess):
            if isinstance(iterated.typ, ListLyraType):  # iteration over list items
                target_typ = iterated.typ.typ
            elif isinstance(iterated.typ, SetLyraType):  # iteration over set items
                target_typ = iterated.typ.typ
            elif isinstance(iterated.typ, DictLyraType):  # iteration over dictionary keys
                iterated = Call(iterated.pp, 'keys', [iterated], SetLyraType(iterated.typ.key_typ))
                target_typ = iterated.typ.typ
        elif isinstance(iterated, Call):
            if iterated.name == 'range':
                assert isinstance(iterated.typ, ListLyraType)
                target_typ = iterated.typ.typ
            elif iterated.name == 'items' or iterated.name == 'keys' or iterated.name == 'values':
                assert isinstance(iterated.typ, SetLyraType)
                target_typ = iterated.typ.typ
            elif iterated.name == 'list':
                assert len(iterated.arguments) == 1
                if isinstance(iterated.arguments[0].typ, ListLyraType):
                    target_typ = iterated.arguments[0].typ.typ
            else:
                error = "The type of the target {} is not yet determinable!".format(iterated)
                raise NotImplementedError(error)
        else:
            error = "The iteration attribute {} is not yet translatable to CFG!".format(iterated)
            raise NotImplementedError(error)
        target = self.visit(node.target, types, target_typ, function_name=function_name)

        body = self._visit_body(node.body, types, function_name=function_name)
        test = Call(pp, 'in', [target, iterated], BooleanLyraType(), forloop=True)
        header = Loop(self._id_gen.next)
        body_in_node = body.in_node
        body_out_node = body.out_node
        body.add_node(header)
        body.in_node = header
        body.add_edge(Conditional(header, test, body_in_node, Edge.Kind.LOOP_IN))
        not_test = Call(pp, 'notin', [target, iterated], BooleanLyraType(), forloop=True)
        body.add_edge(Conditional(header, not_test, None))
        if body_out_node:  # control flow can exit the body
            # add an unconditional LOOP_OUT edge
            body.add_edge(Unconditional(body_out_node, header, Edge.Kind.LOOP_OUT))

        if node.orelse:  # there is an else branch
            orelse = self._visit_body(node.orelse, types, function_name=function_name)
            if orelse.out_node:  # control flow can exit the else
                # add an unconditional DEFAULT edge
                orelse.add_edge(Unconditional(orelse.out_node, None, Edge.Kind.DEFAULT))
            body.append(orelse)

        # handle special edges
        for special, kind in body.special_edges:
            if kind == LooseControlFlowGraph.SpecialEdgeType.CONTINUE:
                body.add_edge(Unconditional(special.source, header, Edge.Kind.LOOP_OUT))
            elif kind == LooseControlFlowGraph.SpecialEdgeType.BREAK:
                body.add_edge(Unconditional(special.source, None, Edge.Kind.LOOP_OUT))
        body.special_edges.clear()

        return body

    # noinspection PyUnusedLocal
    def visit_Break(self, _, types=None, typ=None, function_name='main'):
        """Visitor function for a break statement."""
        dummy = _dummy_node(self._id_gen)
        cfg = LooseControlFlowGraph({dummy}, dummy, None)
        # the type of the special edge is not yet known, set to DEFAULT for now
        edge = Unconditional(dummy, None, Edge.Kind.DEFAULT)
        cfg.special_edges.append((edge, LooseControlFlowGraph.SpecialEdgeType.BREAK))
        return cfg

    # noinspection PyUnusedLocal
    def visit_Continue(self, _, types=None, typ=None, function_name='main'):
        """Visitor function for a continue statement."""
        dummy = _dummy_node(self._id_gen)
        cfg = LooseControlFlowGraph({dummy}, dummy, None)
        # the type of the special edge is not yet known, set to DEFAULT for now
        edge = Unconditional(dummy, None, Edge.Kind.DEFAULT)
        cfg.special_edges.append((edge, LooseControlFlowGraph.SpecialEdgeType.CONTINUE))
        return cfg

    def visit_FunctionDef(self, node, types, function_name):
        for arg in node.args.args:
            annotated = resolve_type_annotation(arg.annotation)
            arg.arg = function_name + "#" + arg.arg
            types[arg.arg] = annotated
        start = _dummy_cfg(self._id_gen)
        body = self._visit_body(node.body, types, loose_in_edges=True, loose_out_edges=True,
                                function_name=function_name)
        end = _dummy_cfg(self._id_gen)
        function_cfg = start.append(body).append(end) if body else start.append(end)
        function_cfg = self._restructure_return_and_raise_edges(function_cfg)
        self._cfgs[function_name] = function_cfg
        return function_cfg

    def visit_Return(self, node, types=None, function_name='main'):
        """Visitor function for a return statement."""
        expressions = self.visit(node.value, types, function_name=function_name)
        return Return(ProgramPoint(node.lineno, node.col_offset), [expressions])

    def _visit_body(self, body, types, loose_in_edges=False, loose_out_edges=False, function_name='main'):
        factory = CFGFactory(self._id_gen)

        for child in body:
            if isinstance(child, ast.Assign):
                if isinstance(child.value, ast.IfExp):  # the value is a conditional expression
                    factory.complete_basic_block()
                    if_cfg = self.visit(child.value, child.targets, None, types, function_name=function_name)
                    factory.append_cfg(if_cfg)
                else:  # normal assignment
                    factory.add_stmts(self.visit(child, types, function_name=function_name))
            elif isinstance(child, ast.AnnAssign):
                if child.value is None:  # only a type annotation
                    annotation = resolve_type_annotation(child.annotation)
                    if isinstance(child.target, ast.Name):
                        types[child.target.id] = annotation
                    elif isinstance(child.target, (ast.Attribute, ast.Subscript)):
                        types[child.target.value] = annotation
                elif isinstance(child.value, ast.IfExp):  # the value is a conditional expression
                    factory.complete_basic_block()
                    annotation = resolve_type_annotation(child.annotation)
                    if_cfg = self.visit(child.value, [child.target], None, types, annotation,
                                        function_name=function_name)
                    factory.append_cfg(if_cfg)
                else:  # normal annotated assignment
                    factory.add_stmts(self.visit(child, types, function_name=function_name))
            elif isinstance(child, ast.AugAssign):
                if isinstance(child.value, ast.IfExp):  # the value is a conditional expression
                    factory.complete_basic_block()
                    if_cfg = self.visit(child.value, [child.target], child.op, types, function_name=function_name)
                    factory.append_cfg(if_cfg)
                else:  # normal augmented assignment
                    factory.add_stmts(self.visit(child, types, function_name=function_name))
            elif isinstance(child, ast.Expr):
                # check other options for AnnAssign (empty value, or IfExp as value)
                factory.add_stmts(self.visit(child, types, function_name=function_name))
            elif isinstance(child, (ast.Raise, ast.Return)):
                factory.add_stmts(self.visit(child, types, function_name=function_name))
                factory.complete_basic_block()
            elif isinstance(child, ast.If):
                factory.complete_basic_block()
                if_cfg = self.visit(child, types, function_name=function_name)
                factory.append_cfg(if_cfg)
            elif isinstance(child, ast.While):
                factory.complete_basic_block()
                while_cfg = self.visit(child, types, function_name=function_name)
                factory.append_cfg(while_cfg)
            elif isinstance(child, ast.For):
                factory.complete_basic_block()
                for_cfg = self.visit(child, types, function_name=function_name)
                factory.append_cfg(for_cfg)
            elif isinstance(child, ast.Break):
                factory.complete_basic_block()
                break_cfg = self.visit(child, types, function_name=function_name)
                factory.append_cfg(break_cfg)
            elif isinstance(child, ast.Continue):
                factory.complete_basic_block()
                cont_cfg = self.visit(child, types, function_name=function_name)
                factory.append_cfg(cont_cfg)
            elif isinstance(child, ast.Pass) and factory.incomplete_block():
                pass
            elif isinstance(child, ast.Pass):
                factory.append_cfg(_dummy_cfg(self._id_gen))
            elif isinstance(child, ast.FunctionDef):
                function_factory = CFGFactory(self._id_gen)
                function_cfg = self.visit_FunctionDef(child, types, child.name)
                function_factory.append_cfg(function_cfg)
            else:
                error = "The statement {} is not yet translatable to CFG!".format(child)
                raise NotImplementedError(error)
        factory.complete_basic_block()

        if not loose_in_edges and factory.cfg and factory.cfg.loose_in_edges:
            factory.prepend_cfg(_dummy_cfg(self._id_gen))
        if not loose_out_edges and factory.cfg and factory.cfg.loose_out_edges:
            factory.append_cfg(_dummy_cfg(self._id_gen))

        return factory.cfg



    # noinspection PyUnusedLocal
    def visit_Module(self, node, types=None, typ=None):
        """Visitor function for a Python module."""
        start = _dummy_cfg(self._id_gen)
        body = self._visit_body(node.body, types, loose_in_edges=True, loose_out_edges=True)
        end = _dummy_cfg(self._id_gen)
        main_cfg = start.append(body).append(end) if body else start.append(end)
        main_cfg = self._restructure_return_and_raise_edges(main_cfg)
        self._cfgs['main'] = main_cfg
        return self._cfgs

    def _restructure_return_and_raise_edges(self, cfg):
        nodes_to_be_removed = []
        for node in cfg.nodes.values():
            if any(isinstance(stmt, (Raise, Return)) for stmt in node.stmts):
                edges_to_be_removed = cfg.get_edges_with_source(node)
                for edge_to_be_removed in edges_to_be_removed:
                    target = edge_to_be_removed.target
                    if len(cfg.get_edges_with_target(target)) == 1: # there is no other edge
                        nodes_to_be_removed.append(edge_to_be_removed.target)
                    cfg.remove_edge(edge_to_be_removed)
                cfg.add_edge(Unconditional(node, cfg.out_node)) # connect the node to the exit node
        for node_to_be_removed in nodes_to_be_removed:
            cfg.remove_node(node_to_be_removed)
        return cfg


def ast_to_cfg(root, function_name='main'):
    """Generate a CFG from an AST.

    :param root: root node of the AST
    :param function_name: the function whose CFG will be generated
    :return: the CFG generated from the given AST for the function function_name
    """
    return ast_to_cfgs(root)[function_name]


def ast_to_cfgs(root):
    """Generate a CFG for each user-defined function from an AST.

    :param root: root node of the AST
    :return: a mapping of function names to the corresponding CFGs generated from the given AST and the corresponding
    function definition
    """
    loose_cfgs = CFGVisitor().visit(root, dict())
    cfgs = {name: loose_cfg.eject() for name, loose_cfg in loose_cfgs.items()}
    return cfgs

def ast_to_function_args(root):

    function_args = {'main': None}
    for child in root.body:
        if isinstance(child, ast.FunctionDef):
            function_name = child.name
            args = []
            for arg in child.args.args:
                annotated = resolve_type_annotation(arg.annotation)
                args.append(VariableIdentifier(annotated, arg.arg))
            function_args[function_name] = args
    return function_args


def source_to_cfg(code: str, function_name='main'):
    """Generate a CFG from a Python program.

    :param code: Python program
    :param function_name: the function whose CFG will be generated
    :return: the CFG generated from the given Python program for the function function_name
    """
    return source_to_cfgs(code)[function_name]


def source_to_cfgs(code: str):
    """Generate a CFG for each user-defined function from a Python program.

    :param code: Python program
    :return: the CFG generated for each user-defined function from the given Python program
    """
    root_node = ast.parse(code)
    return ast_to_cfgs(root_node)


def main(args):
    optparser = optparse.OptionParser(usage="python3 -m frontend.cfg_generator [options] [string]")
    optparser.add_option("-f", "--file", help="Read a code snippet from the specified file")
    optparser.add_option("-l", "--label", help="The label for the visualization")

    options, args = optparser.parse_args(args)
    if options.file:
        with open(options.file) as instream:
            code = instream.read()
        label = options.file
    elif len(args) == 2:
        code = args[1] + "\n"
        label = "<code read from command line parameter>"
    else:
        print("Expecting Python code on stdin...")
        code = sys.stdin.read()
        label = "<code read from stdin>"
    if options.label:
        label = options.label

    cfg = source_to_cfg(code)
    CFGRenderer().render(cfg, label=label)


if __name__ == '__main__':
    main(sys.argv)
