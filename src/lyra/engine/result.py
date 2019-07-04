from itertools import zip_longest
from typing import List

from lyra.abstract_domains.state import State
from lyra.core.cfg import Node, ControlFlowGraph, Edge


class AnalysisResult:
    def __init__(self, cfg: ControlFlowGraph):
        """Analysis result representation.

        :param cfg: analyzed control flow graph
        """
        self._cfg = cfg
        self._result = dict()

    @property
    def cfg(self):
        return self._cfg

    @property
    def result(self):
        return self._result

    def get_node_result(self, node: Node) -> List[List[State]]:
        """Get the analysis result for a node.

        :param node: analyzed node
        :return: list of states representing the result of the analysis for the block
        """
        return self.result[node]

    def set_node_result(self, node: Node, states: List[List[State]]) -> None:
        """Set the analysis result for a node.

        :param node: analyzed node
        :param states: list of states representing the result of the analysis for the block
        """
        self.result[node] = states

    def merge(self, other_result):
        for node in self.result.keys():
            current_states_list = self.result[node]
            other_states_list = other_result.result[node]
            length = len(current_states_list)
            result_list = [[0] * 2 for i in range(length)]
            for index in range(length):
                current_state = current_states_list[index]
                other_state = other_states_list[index]
                result_list[index][0] = current_state
                result_list[index][1] = other_state
            self.set_node_result(node, result_list)


    def __str__(self):
        """Analysis result string representation.

        :return: string representing the result of the analysis
        """
        visited, pending = set(), list()
        pending.append(self.cfg.in_node)
        result = []
        while pending:
            current = pending.pop()    # retrieve the current pending item
            if current not in visited:
                if isinstance(current, Node):   # print a node
                    result.append("********* {} *********".format(current))
                    states = self.get_node_result(current)
                    node = [item for items in zip_longest(states, current.stmts)
                            for item in items if item is not None]
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
