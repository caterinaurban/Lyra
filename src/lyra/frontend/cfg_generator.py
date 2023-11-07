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
        self._fdefs = dict()

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
    def visit_Constant(self, node, types=None, libraries=None, typ=None, fname=''):
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.value, bool):
            expr = Literal(BooleanLyraType(), str(node.value))
            return LiteralEvaluation(pp, expr)
        elif isinstance(node.value, int):
            expr = Literal(IntegerLyraType(), str(node.n))
            return LiteralEvaluation(pp, expr)
        elif isinstance(node.value, float):
            expr = Literal(FloatLyraType(), str(node.n))
            return LiteralEvaluation(pp, expr)
        elif isinstance(node.value, str):
            expr = Literal(StringLyraType(), node.s)
            return LiteralEvaluation(pp, expr)
        raise NotImplementedError(f"Num of type {node.n.__class__.__name__} is unsupported!")

    # noinspection PyUnusedLocal
    def visit_Num(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a number (integer, float, or complex).
        The n attribute stores the value, already converted to the relevant type."""
        import warnings
        warnings.warn('Class deprecated since Python 3.8', DeprecationWarning)
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.n, int):
            expr = Literal(IntegerLyraType(), str(node.n))
            return LiteralEvaluation(pp, expr)
        elif isinstance(node.n, float):
            expr = Literal(FloatLyraType(), str(node.n))
            return LiteralEvaluation(pp, expr)
        raise NotImplementedError(f"Num of type {node.n.__class__.__name__} is unsupported!")

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def visit_Str(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a string. The s attribute stores the value."""
        import warnings
        warnings.warn('Class deprecated since Python 3.8', DeprecationWarning)
        pp = ProgramPoint(node.lineno, node.col_offset)
        expr = Literal(StringLyraType(), node.s)
        return LiteralEvaluation(pp, expr)

    def visit_List(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a list.
        The elts attribute stores a list of nodes representing the elements.
        The ctx attribute is Store if the container is an assignment target, and Load otherwise."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, list):   # this comes from a subscript
            items = [self.visit(item, types, libraries, typ[1], fname=fname) for item in node.elts]
            itm_typ = items[0].typ if isinstance(typ[1], list) else typ[1]
            return ListDisplayAccess(pp, ListLyraType(itm_typ), items)
        if isinstance(typ, ListLyraType):
            items = [self.visit(item, types, libraries, typ.typ, fname=fname) for item in node.elts]
            return ListDisplayAccess(pp, typ, items)
        else:
            items = [self.visit(item, types, libraries, None, fname=fname) for item in node.elts]
            if isinstance(items[0], LiteralEvaluation):
                itm_typ = items[0].literal.typ
            else:
                itm_typ = items[0].typ
            return ListDisplayAccess(pp, ListLyraType(itm_typ), items)

    def visit_Tuple(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a tuple.
        The elts attribute stores a list of nodes representing the elements.
        The ctx attribute is Store if the container is an assignment target, and Load otherwise."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, list):   # this comes from a subscript
            items = [self.visit(item, types, libraries, None, fname=fname) for item in node.elts]
            return TupleDisplayAccess(pp, TupleLyraType([]), items)     # TODO: fix me
        if isinstance(typ, TupleLyraType):
            zipped = zip(node.elts, typ.typs)
            items = [self.visit(item, types, libraries, i_typ, fname=fname) for item, i_typ in zipped]
            return TupleDisplayAccess(pp, typ, items)
        else:
            items = [self.visit(item, types, libraries, None, fname=fname) for item in node.elts]
            typs = list()
            for item in items:
                if isinstance(item, LiteralEvaluation):
                    typs.append(item.literal.typ)
                else:
                    typs.append(item.typ)
            return TupleDisplayAccess(pp, TupleLyraType(typs), items)

    def visit_Set(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a set.
        The elts attribute stores a list of nodes representing the elements."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, list):   # this comes from a subscript
            items = [self.visit(item, types, libraries, typ[1], fname=fname) for item in node.elts]
            itm_typ = items[0].typ if isinstance(typ[1], list) else typ[1]
            return SetDisplayAccess(pp, SetLyraType(itm_typ), items)
        if isinstance(typ, SetLyraType):
            items = [self.visit(item, types, libraries, typ.typ, fname=fname) for item in node.elts]
            return SetDisplayAccess(pp, typ, items)
        else:
            items = [self.visit(item, types, libraries, None, fname=fname) for item in node.elts]
            if isinstance(items[0], LiteralEvaluation):
                itm_typ = items[0].literal.typ
            else:
                itm_typ = items[0].typ
            return SetDisplayAccess(pp, SetLyraType(itm_typ), items)

    def visit_Dict(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a dictionary.
        The attributes keys and values store lists of nodes with matching order
        representing the keys and the values, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(typ, list):   # this comes from a subscript
            keys = [self.visit(key, types, libraries, typ[0], fname=fname) for key in node.keys]
            values = [self.visit(value, types, libraries, typ[1], fname=fname) for value in node.values]
            val_typ = values[0].typ if isinstance(typ[1], list) else typ[1]
            return DictDisplayAccess(pp, DictLyraType(typ[0], val_typ), keys, values)
        if isinstance(typ, DictLyraType):
            keys = [self.visit(key, types, libraries, typ.key_typ, fname=fname) for key in node.keys]
            values = [self.visit(value, types, libraries, typ.val_typ, fname=fname) for value in node.values]
            return DictDisplayAccess(pp, typ, keys, values)
        else:
            keys = [self.visit(key, types, libraries, None, fname=fname) for key in node.keys]
            if isinstance(keys[0], LiteralEvaluation):
                key_typ = keys[0].literal.typ
            else:
                key_typ = keys[0].typ
            values = [self.visit(value, types, libraries, None, fname=fname) for value in node.values]
            if isinstance(values[0], LiteralEvaluation):
                val_typ = values[0].literal.typ
            else:
                val_typ = values[0].typ
            return DictDisplayAccess(pp, DictLyraType(key_typ, val_typ), keys, values)

    # noinspection PyUnusedLocal
    def visit_NameConstant(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for True, False or None.
        The value attribute stores the constant."""
        import warnings
        warnings.warn('Class deprecated since Python 3.8', DeprecationWarning)
        if isinstance(node.value, bool):
            pp = ProgramPoint(node.lineno, node.col_offset)
            expr = Literal(BooleanLyraType(), str(node.value))
            return LiteralEvaluation(pp, expr)
        raise NotImplementedError(f"Constant {node.value.__class__.__name__} is unsupported!")

    # Variables

    def visit_Name(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a variable name.
        The attribute id stores the name as a string.
        The attribute ctx is Store (to assign a new value to the variable),
        Load (to load the value of the variable), or Del (to delete the variable)."""
        name = fname + "#" + node.id if fname else node.id
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.ctx, ast.Store):
            if name not in types:
                if typ:
                    types[name] = typ
                else:
                    raise ValueError(f"Missing type annotation for variable {name}!")
            expr = VariableIdentifier(types[name], name)
            return VariableAccess(pp, types[name], expr)
        if isinstance(node.ctx, ast.Load):
            if name in libraries:
                return LibraryAccess(pp, libraries[name], name)
            if name in types:
                _name = name
            else:
                _name = name.replace(fname + '#', '')
            assert _name in types
            # assert types[name] == typ or typ is None
            expr = VariableIdentifier(types[_name], _name)
            return VariableAccess(pp, types[_name], expr)
        assert isinstance(node.ctx, ast.Del)
        raise NotImplementedError(f"Name deletion is unsupported!")

    # Expressions

    # noinspection PyUnusedLocal
    def visit_Expr(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for an expression statement (whose return value is unused).
        The attribute value stored another AST node."""
        return self.visit(node.value, types, libraries, fname=fname)

    def visit_UnaryOp(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a unary operation.
        The attributes op and operand store the operator
        and any expression node, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        name = type(node.op).__name__.lower()
        argument = self.visit(node.operand, types, libraries, typ, fname=fname)
        return Call(pp, name, [argument], typ)

    def visit_BinOp(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a binary operation.
        The attributes op, left, and right store the operator
        and any expression nodes, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        name = type(node.op).__name__.lower()
        left = self.visit(node.left, types, libraries, typ, fname=fname)
        right = self.visit(node.right, types, libraries, typ, fname=fname)
        return Call(pp, name, [left, right], typ)

    def visit_BoolOp(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a boolean operation.
        The attributes op and values store the operand
        and a list of any expression node representing the operand involved, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        name = type(node.op).__name__.lower()
        arguments = [self.visit(val, types, libraries, typ, fname=fname) for val in node.values]
        return Call(pp, name, arguments, typ)

    def visit_Compare(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a comparison operation.
        The attributes left, ops, and comparators store the first value in the comparison,
        the list of operators, and the list of compared values after the first."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert isinstance(typ, BooleanLyraType)  # we expect typ to be a BooleanLyraType
        left = self.visit(node.left, types, libraries, None, fname=fname)
        name = type(node.ops[0]).__name__.lower()
        second = self.visit(node.comparators[0], types, libraries, None, fname=fname)
        result = Call(pp, name, [left, second], typ)
        for op, comparator in zip(node.ops[1:], node.comparators[1:]):
            name = type(op).__name__.lower()
            right = self.visit(comparator, types, libraries, None, fname=fname)
            current = Call(pp, name, [second, right], typ)
            result = Call(pp, 'and', [result, current], typ)
            second = right
        return result

    def visit_Call(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a call.
        The attribute func stores the function being called (often a Name or Attribute object).
        The attribute args stores a list fo the arguments passed by position."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        if isinstance(node.func, ast.Name):
            name: str = node.func.id
            if name == 'bool' or name == 'int' or name == 'str':
                arguments = [self.visit(arg, types, libraries, typ, fname=fname) for arg in node.args]
                return Call(pp, name, arguments, typ)
            if name == 'input':
                typ = StringLyraType
                arguments = [self.visit(arg, types, libraries, typ(), fname=fname) for arg in node.args]
                return Call(pp, name, arguments, typ())
            if name == 'range':
                typ = IntegerLyraType
                arguments = [self.visit(arg, types, libraries, typ(), fname=fname) for arg in node.args]
                return Call(pp, name, arguments, ListLyraType(typ()))
            arguments = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
            return Call(pp, name, arguments, typ)
        elif isinstance(node.func, ast.Attribute):
            name: str = node.func.attr
            if name == 'append':
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
                assert isinstance(arguments[0].typ, ListLyraType)
                args = [self.visit(arg, types, libraries, arguments[0].typ.typ, fname=fname) for arg in node.args]
                arguments.extend(args)
                return Call(pp, name, arguments, arguments[0].typ)
            if name == 'count':  # str.count(sub, start= 0,end=len(string))
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]  # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, (StringLyraType, ListLyraType))
                return Call(pp, name, arguments, IntegerLyraType())
            if name == 'find':  # str.find(str, beg=0, end=len(string))
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]  # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, StringLyraType)
                return Call(pp, name, arguments, IntegerLyraType())
            if name == 'get':  # dict.get(key[, value])
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, DictLyraType)
                return Call(pp, name, arguments, arguments[0].typ.val_typ)
            if name == 'items':
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, DictLyraType)
                tuple_typ = TupleLyraType([arguments[0].typ.key_typ, arguments[0].typ.val_typ])
                return Call(pp, name, arguments, SetLyraType(tuple_typ))
            if name == 'keys':
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, DictLyraType)
                return Call(pp, name, arguments, SetLyraType(arguments[0].typ.key_typ))
            if name == 'lstrip' or name == 'strip' or name == 'rstrip':
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, StringLyraType)
                return Call(pp, name, arguments, arguments[0].typ)
            if name == 'split':  # str.split([sep[, maxsplit]])
                if isinstance(typ, list):    # this comes from a subscript
                    _typ = ListLyraType(typ[0])
                else:
                    _typ = typ
                assert isinstance(_typ, ListLyraType)  # we expect type to be a ListLyraType
                arguments = [self.visit(node.func.value, types, libraries, _typ.typ, fname=fname)]  # target
                args_typs = zip(node.args, [_typ.typ, IntegerLyraType()])
                args = [self.visit(arg, types, libraries, arg_typ, fname=fname) for arg, arg_typ in args_typs]
                arguments.extend(args)
                return Call(pp, name, arguments, typ)
            if name == 'values':
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, DictLyraType)
                return Call(pp, name, arguments, SetLyraType(arguments[0].typ.val_typ))
            if name == 'update':
                arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
                args = [self.visit(arg, types, libraries, None, fname=fname) for arg in node.args]
                arguments.extend(args)
                assert isinstance(arguments[0].typ, SetLyraType)
                return Call(pp, name, arguments, arguments[0].typ)
            arguments = [self.visit(node.func.value, types, libraries, None, fname=fname)]     # target
            # TODO: deal with keywords
            arguments.extend([self.visit(arg, types, libraries, None, fname=fname) for arg in node.args])
            return Call(pp, name, arguments, typ)

    def visit_IfExp(self, node, targets, op=None, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for an if expression.
        The components of the expression are stored in the attributes test, body, and orelse."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        _pp = ProgramPoint(-node.lineno, -node.col_offset)
        then = CFGFactory(self._id_gen)
        body = self.visit(node.body, types, libraries, typ, fname=fname)
        assignments = list()
        for target in targets:
            left = self.visit(target, types, libraries, typ, fname=fname)
            if op:
                name = type(op).__name__.lower()
                value = Call(pp, name, [left, body], left.typ)
                assignments.append(Assignment(pp, left, value))
            else:
                assignments.append(Assignment(pp, left, body))
        then.add_stmts(assignments)
        then.complete_basic_block()
        then = then.cfg
        test = self.visit(node.test, types, libraries, BooleanLyraType(), fname=fname)
        then.add_edge(Conditional(None, test, then.in_node, Edge.Kind.IF_IN))
        then.add_edge(Unconditional(then.out_node, None, Edge.Kind.IF_OUT))
        orelse = CFGFactory(self._id_gen)
        body = self.visit(node.orelse, types, libraries, typ, fname=fname)
        assignments = list()
        for target in targets:
            left = self.visit(target, types, libraries, typ, fname=fname)
            if op:
                name = type(op).__name__.lower()
                value = Call(pp, name, [left, body], left.typ)
                assignments.append(Assignment(pp, left, value))
            else:
                assignments.append(Assignment(pp, left, body))
        orelse.add_stmts(assignments)
        orelse.complete_basic_block()
        orelse = orelse.cfg
        not_test = Call(_pp, 'not', [test], BooleanLyraType())
        orelse.add_edge(Conditional(None, not_test, orelse.in_node, Edge.Kind.IF_IN))
        orelse.add_edge(Unconditional(orelse.out_node, None, Edge.Kind.IF_OUT))
        return then.combine(orelse)

    # Subscripting

    def visit_Subscript(self, node: ast.Subscript, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a subscript.
        The attribute value stores the target of the subscript (often a Name).
        The attribute slice is one of Index, Slice, or ExtSlice.
        The attribute ctx is Load, Store, or Del."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        constant = isinstance(node.slice, ast.Constant)
        name = isinstance(node.slice, ast.Name)
        binop = isinstance(node.slice, ast.BinOp)
        subscript = isinstance(node.slice, ast.Subscript)
        list = isinstance(node.slice, ast.List)
        if constant or name or binop or subscript or list:
            key = self.visit(node.slice, types, libraries, None, fname=fname)
            if isinstance(key, LiteralEvaluation):
                _typ = key.literal.typ
            else:
                _typ = key.typ
            target = self.visit(node.value, types, libraries, [_typ, typ], fname=fname)
            if isinstance(target.typ, DictLyraType):
                return SubscriptionAccess(pp, target.typ.val_typ, target, key)
            elif isinstance(target.typ, ListLyraType):
                return SubscriptionAccess(pp, target.typ.typ, target, key)
            else:  # String
                return SubscriptionAccess(pp, target.typ, target, key)
        elif isinstance(node.slice, ast.Slice):
            value = self.visit(node.value, types, libraries, None, fname=fname)
            lower = None
            if node.slice.lower:
                lower = self.visit(node.slice.lower, types, libraries, None, fname=fname)
            upper = None
            if node.slice.upper:
                upper = self.visit(node.slice.upper, types, libraries, None, fname=fname)
            step = None
            if node.slice.step:
                step = self.visit(node.slice.step, types, libraries, None, fname=fname)
            return SlicingAccess(pp, typ, value, lower, upper, step)
        raise NotImplementedError(f"Subscription {node.slice.__class__.__name__} is unsupported!")

    # Statements

    def visit_Assign(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for an assignment.
        The attribute targets stores a list of targets of the assignment.
        The attribute value stores the assigned value."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert typ is None     # we expect typ to be None
        assert len(node.targets) == 1
        target = self.visit(node.targets[0], types=types, libraries=libraries, typ=None, fname=fname)
        value = self.visit(node.value, types=types, libraries=libraries, typ=target.typ, fname=fname)
        return Assignment(pp, target, value)

    def visit_AnnAssign(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for an assignment with a type annotation.
        The attribute target stores the target of the assignment (a Name, Attribute, or Subscript).
        The attribute annotation stores the type annotation (a Str or Name).
        The attribute value optionally stores the assigned value."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert typ is None  # we expect typ to be None
        annotated = resolve_type_annotation(node.annotation)
        target = self.visit(node.target, types=types, libraries=libraries, typ=annotated, fname=fname)
        value = self.visit(node.value, types=types, libraries=libraries, typ=annotated, fname=fname)
        return Assignment(pp, target, value)

    def visit_AugAssign(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for an augmented assignment.
        The attribute target stores the target of the assignment (a Name, Attribute, or Subscript).
        The attributes op and value store the operation and the assigned value, respectively."""
        pp = ProgramPoint(node.lineno, node.col_offset)
        assert typ is None  # we expect typ to be None
        target = self.visit(node.target, types=types, libraries=libraries, typ=None, fname=fname)
        name = type(node.op).__name__.lower()
        right = self.visit(node.value, types=types, libraries=libraries, typ=None, fname=fname)
        value = Call(pp, name, [target, right], target.typ)
        return Assignment(pp, target, value)

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def visit_Raise(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for an exception raise.
        The attribute exc stores the exception object to be raised
        (normally a Call or Name, or None for a standalone raise)."""
        return Raise(ProgramPoint(node.lineno, node.col_offset))

    def visit_Import(self, node, types=None, libraries=None, fname=''):
        """Visitor function for a library import.
        """
        pp = ProgramPoint(node.lineno, node.col_offset)
        library = node.names[0].name
        name = node.names[0].asname
        libraries[name] = library
        if name:
            return Import(pp, library, name)
        else:
            return Import(pp, library, library)

    # Control Flow

    def visit_If(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for an if statement.
        The attribute test stores a single AST node.
        The attributes body and orelse each store a list of AST nodes to be executed."""
        pp = ProgramPoint(node.test.lineno, node.test.col_offset)
        _pp = ProgramPoint(-node.test.lineno, -node.test.col_offset)

        body = self._visit_body(node.body, types, libraries, fname=fname)
        test = self.visit(node.test, types=types, libraries=libraries, typ=BooleanLyraType(), fname=fname)
        body.add_edge(Conditional(None, test, body.in_node, Edge.Kind.IF_IN))
        if body.out_node:  # control flow can exit the body
            # add an unconditional IF_OUT edge
            body.add_edge(Unconditional(body.out_node, None, Edge.Kind.IF_OUT))

        if node.orelse:  # there is an else branch
            orelse = self._visit_body(node.orelse, types, libraries, fname=fname)
            not_test = Call(_pp, 'not', [test], BooleanLyraType())
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
            not_test = Call(_pp, 'not', [test], BooleanLyraType())
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

    def visit_While(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a while statement.
        The attribute test stores a single AST node.
        The attributes body and orelse each store a list of AST nodes to be executed."""
        pp = ProgramPoint(node.test.lineno, node.test.col_offset)
        _pp = ProgramPoint(-node.test.lineno, -node.test.col_offset)

        body = self._visit_body(node.body, types, libraries, fname=fname)
        test = self.visit(node.test, types=types, libraries=libraries, typ=BooleanLyraType(), fname=fname)
        header = Loop(self._id_gen.next)
        body_in_node = body.in_node
        body_out_node = body.out_node
        body.add_node(header)
        body.in_node = header
        body.add_edge(Conditional(header, test, body_in_node, Edge.Kind.LOOP_IN))
        not_test = Call(_pp, 'not', [test], BooleanLyraType())
        body.add_edge(Conditional(header, not_test, None))
        if body_out_node:  # control flow can exit the body
            # add an unconditional LOOP_OUT edge
            body.add_edge(Unconditional(body_out_node, header, Edge.Kind.LOOP_OUT))

        if node.orelse:  # there is an else branch
            orelse = self._visit_body(node.orelse, types, libraries, fname=fname)
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

    def visit_For(self, node, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a for statement.
        The attribute target stores the variable(s) the loop assigns to
        (as a single Name, Tuple, or List node).
        The attribute iter stores a single AST node representing the item to be looped over.
        The attributes body and orelse each store a list of AST nodes to be executed."""
        pp = ProgramPoint(node.target.lineno, node.target.col_offset)
        _pp = ProgramPoint(-node.target.lineno, -node.target.col_offset)

        iterated = self.visit(node.iter, types=types, libraries=libraries, typ=None, fname=fname)
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
        target = self.visit(node.target, types=types, libraries=libraries, typ=target_typ, fname=fname)

        body = self._visit_body(node.body, types, libraries, fname=fname)
        test = Call(pp, 'in', [target, iterated], BooleanLyraType(), forloop=True)
        header = Loop(self._id_gen.next)
        body_in_node = body.in_node
        body_out_node = body.out_node
        body.add_node(header)
        body.in_node = header
        body.add_edge(Conditional(header, test, body_in_node, Edge.Kind.LOOP_IN))
        not_test = Call(_pp, 'notin', [target, iterated], BooleanLyraType(), forloop=True)
        body.add_edge(Conditional(header, not_test, None))
        if body_out_node:  # control flow can exit the body
            # add an unconditional LOOP_OUT edge
            body.add_edge(Unconditional(body_out_node, header, Edge.Kind.LOOP_OUT))

        if node.orelse:  # there is an else branch
            orelse = self._visit_body(node.orelse, types=types, libraries=libraries, fname=fname)
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
    def visit_Break(self, _, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a break statement."""
        dummy = _dummy_node(self._id_gen)
        cfg = LooseControlFlowGraph({dummy}, dummy, None)
        # the type of the special edge is not yet known, set to DEFAULT for now
        edge = Unconditional(dummy, None, Edge.Kind.DEFAULT)
        cfg.special_edges.append((edge, LooseControlFlowGraph.SpecialEdgeType.BREAK))
        return cfg

    # noinspection PyUnusedLocal
    def visit_Continue(self, _, types=None, libraries=None, typ=None, fname=''):
        """Visitor function for a continue statement."""
        dummy = _dummy_node(self._id_gen)
        cfg = LooseControlFlowGraph({dummy}, dummy, None)
        # the type of the special edge is not yet known, set to DEFAULT for now
        edge = Unconditional(dummy, None, Edge.Kind.DEFAULT)
        cfg.special_edges.append((edge, LooseControlFlowGraph.SpecialEdgeType.CONTINUE))
        return cfg

    def visit_FunctionDef(self, node: ast.FunctionDef, types, libraries, fname):
        """Visit function for a function definition.

        class FunctionDef(name, args, body, decorator_list, returns)
            name is a raw string of the function name.
            args is a arguments node.
            body is the list of nodes inside the function.
            decorator_list is the list of decorators to be applied.
            returns is the return annotation.
        """
        for arg in node.args.args:
            annotated = resolve_type_annotation(arg.annotation)
            arg.arg = fname + "#" + arg.arg
            types[arg.arg] = annotated
        types[fname + "#return"] = resolve_type_annotation(node.returns)
        start = _dummy_cfg(self._id_gen)
        body = self._visit_body(node.body, types, libraries, True, True, fname)
        end = _dummy_cfg(self._id_gen)
        fun_cfg = start.append(body).append(end) if body else start.append(end)
        # fun_cfg = self._restructure_return_and_raise_edges(fun_cfg)
        self._cfgs[fname] = fun_cfg
        return fun_cfg

    def visit_Return(self, node, types=None, libraries=None, fname=''):
        """Visitor function for a return statement."""
        typ = types[fname + "#return"]
        expressions = self.visit(node.value, typ=typ, types=types, libraries=libraries, fname=fname)
        return Return(ProgramPoint(node.lineno, node.col_offset), [expressions])

    def _visit_body(self, body, types, libraries, loose_in_edges=False, loose_out_edges=False, fname=''):
        factory = CFGFactory(self._id_gen)

        for child in body:
            if isinstance(child, ast.Assign):
                if isinstance(child.value, ast.IfExp):  # the value is a conditional expression
                    factory.complete_basic_block()
                    targets = child.targets
                    if_cfg = self.visit(child.value, targets, op=None, types=types, libraries=libraries, fname=fname)
                    factory.append_cfg(if_cfg)
                else:  # normal assignment
                    factory.add_stmts(self.visit(child, types=types, libraries=libraries, fname=fname))
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
                    targets = [child.target]
                    if_cfg = self.visit(child.value, targets, None, types, libraries, annotation, fname)
                    factory.append_cfg(if_cfg)
                else:  # normal annotated assignment
                    factory.add_stmts(self.visit(child, types, libraries, fname=fname))
            elif isinstance(child, ast.AugAssign):
                if isinstance(child.value, ast.IfExp):  # the value is a conditional expression
                    factory.complete_basic_block()
                    targets = [child.target]
                    if_cfg = self.visit(child.value, targets, child.op, types=types, libraries=libraries, fname=fname)
                    factory.append_cfg(if_cfg)
                else:  # normal augmented assignment
                    factory.add_stmts(self.visit(child, types=types, libraries=libraries, fname=fname))
            elif isinstance(child, ast.Expr):
                # check other options for AnnAssign (empty value, or IfExp as value)
                factory.add_stmts(self.visit(child, types=types, libraries=libraries, fname=fname))
            elif isinstance(child, (ast.Raise, ast.Return)):
                factory.add_stmts(self.visit(child, types=types, libraries=libraries, fname=fname))
                factory.complete_basic_block()
            elif isinstance(child, ast.If):
                factory.complete_basic_block()
                if_cfg = self.visit(child, types=types, libraries=libraries, fname=fname)
                factory.append_cfg(if_cfg)
            elif isinstance(child, ast.While):
                factory.complete_basic_block()
                while_cfg = self.visit(child, types=types, libraries=libraries, fname=fname)
                factory.append_cfg(while_cfg)
            elif isinstance(child, ast.For):
                factory.complete_basic_block()
                for_cfg = self.visit(child, types=types, libraries=libraries, fname=fname)
                factory.append_cfg(for_cfg)
            elif isinstance(child, ast.Break):
                factory.complete_basic_block()
                break_cfg = self.visit(child, types=types, libraries=libraries, fname=fname)
                factory.append_cfg(break_cfg)
            elif isinstance(child, ast.Continue):
                factory.complete_basic_block()
                cont_cfg = self.visit(child, types=types, libraries=libraries, fname=fname)
                factory.append_cfg(cont_cfg)
            elif isinstance(child, ast.Pass) and factory.incomplete_block():
                pass
            elif isinstance(child, ast.Pass):
                factory.append_cfg(_dummy_cfg(self._id_gen))
            elif isinstance(child, ast.FunctionDef):
                self._fdefs[child.name] = child
            elif isinstance(child, ast.Import):
                factory.add_stmts(self.visit(child, types, libraries, fname=fname))
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
    def visit_Module(self, node, types=None, libraries=None, typ=None):
        """Visitor function for a Python module."""
        start = _dummy_cfg(self._id_gen)
        body = self._visit_body(node.body, types, libraries, loose_in_edges=True, loose_out_edges=True)
        end = _dummy_cfg(self._id_gen)
        main_cfg = start.append(body).append(end) if body else start.append(end)
        # main_cfg = self._restructure_return_and_raise_edges(main_cfg)
        self._cfgs[''] = main_cfg
        for fdef, child in self._fdefs.items():
            fun_factory = CFGFactory(self._id_gen)
            fun_cfg = self.visit_FunctionDef(child, types, libraries, child.name)
            fun_factory.append_cfg(fun_cfg)
        return self._cfgs

    # def _restructure_return_and_raise_edges(self, cfg):
    #     nodes_to_be_removed = []
    #     for node in cfg.nodes.values():
    #         if any(isinstance(stmt, (Raise, Return)) for stmt in node.stmts):
    #             edges_to_be_removed = cfg.get_edges_with_source(node)
    #             for edge_to_be_removed in edges_to_be_removed:
    #                 target = edge_to_be_removed.target
    #                 if len(cfg.get_edges_with_target(target)) == 1: # there is no other edge
    #                     nodes_to_be_removed.append(edge_to_be_removed.target)
    #                 cfg.remove_edge(edge_to_be_removed)
    #             cfg.add_edge(Unconditional(node, cfg.out_node)) # connect the node to the exit node
    #     for node_to_be_removed in nodes_to_be_removed:
    #         cfg.remove_node(node_to_be_removed)
    #     return cfg


def ast_to_cfgs(root):
    """Generate a CFG for each user-defined function from an AST.

    :param root: root node of the AST
    :return: mapping of function names to the corresponding CFG generated from the given AST
    """
    loose_cfgs = CFGVisitor().visit(root, dict(), dict())
    cfgs = {name: loose_cfg.eject() for name, loose_cfg in loose_cfgs.items()}
    return cfgs


def ast_to_fargs(root):
    fargs = {'': None}
    for child in root.body:
        if isinstance(child, ast.FunctionDef):
            fname = child.name
            args = []
            for arg in child.args.args:
                annotated = resolve_type_annotation(arg.annotation)
                args.append(VariableIdentifier(annotated, arg.arg))
            fargs[fname] = args
    return fargs


def source_to_cfg(code: str, fname=''):
    """Generate a CFG from a Python program.

    :param code: Python program
    :param fname: the function whose CFG will be generated
    :return: the CFG generated from the given Python program for the function fname
    """
    return source_to_cfgs(code)[fname]


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
