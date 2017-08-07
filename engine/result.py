from itertools import zip_longest
from typing import List

from abstract_domains.state import State
from core.cfg import Node, ControlFlowGraph, Edge, Conditional
from core.statements import ProgramPoint


class AnalysisResult:
    def __init__(self, cfg: ControlFlowGraph):
        """Analysis result representation.
        
        :param cfg: analyzed control flow graph
        """
        self._cfg = cfg

        # primary data structure holding {Node: List[State]}
        self._node_result = dict()

        # index data structures
        self._result_before_pp = dict()
        self._result_after_pp = dict()
        self._result_before_conditional_edge = dict()
        self._result_after_conditional_edge = dict()

    @property
    def cfg(self):
        return self._cfg

    @property
    def nodes(self):
        return self._node_result.keys()

    def get_node_result(self, node: Node) -> List[State]:
        """Get the analysis result for a node.
        
        :param node: analyzed node
        :return: list of states representing the result of the analysis for the block
        """
        return self._node_result[node]

    def set_node_result(self, node: Node, states: List[State]) -> None:
        """Set the analysis result for a node.
        
        :param node: analyzed node
        :param states: list of states representing the result of the analysis for the block
        """
        self._node_result[node] = states

        # update index data structures
        # -> index the state before and after each statement
        if node.stmts:
            for stmt, state in zip(node.stmts, states[:-1]):
                self._result_before_pp[stmt.pp] = state
            for stmt, state in zip(node.stmts, states[1:]):
                self._result_after_pp[stmt.pp] = state
        # -> index the state before and after each edge
        for e in self.cfg.in_edges(node):
            if isinstance(e, Conditional):
                # we have to index with pair (program point, kind) since they are multiple edges for a single condition)
                self._result_after_conditional_edge[(e.condition.pp, e.kind)] = states[0]
        for e in self.cfg.out_edges(node):
            if isinstance(e, Conditional):
                # we have to index with pair (program point, kind) since they are multiple edges for a single condition)
                self._result_before_conditional_edge[(e.condition.pp, e.kind)] = states[-1]

    def get_result_before(self, pp: ProgramPoint, edge_kind: Edge.Kind = None) -> State:
        """Get the analysis result before a program point."""
        if edge_kind:
            return self._result_before_conditional_edge[(pp, edge_kind)]
        else:
            return self._result_before_pp[pp]

    def get_result_after(self, pp: ProgramPoint, edge_kind: Edge.Kind = None) -> State:
        """Get the analysis result after a program point."""
        if edge_kind:
            return self._result_after_conditional_edge[(pp, edge_kind)]
        else:
            return self._result_after_pp[pp]

    def __str__(self):
        """Analysis result string representation.
        
        :return: string representing the result of the analysis
        """
        visited, pending = set(), list()
        pending.append(self.cfg.in_node)
        result = []
        while pending:
            current = pending.pop()  # retrieve the current pending item
            if current not in visited:
                if isinstance(current, Node):  # print a node
                    result.append("********* {} *********".format(current))
                    states = self.get_node_result(current)
                    node = [item for items in zip_longest(states, current.stmts) for item in items if item is not None]
                    result.append("\n".join("{}".format(item) for item in node))
                    # retrieve out edges of the node and add them to the pending items
                    for edge in self.cfg.out_edges(current):
                        if edge not in visited:
                            pending.append(edge)
                elif isinstance(current, Edge):
                    result.append("\n{0!s}\n".format(current))
                    # retrieve target of the edge and add it to the pending items
                    if current.target not in visited:
                        pending.append(current.target)
                visited.add(current)
        return "\n".join(res for res in result)
