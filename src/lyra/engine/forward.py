"""
Forward Analysis Engine
=======================

:Author: Caterina Urban
"""

from collections import deque
from copy import deepcopy
from queue import Queue
from typing import Optional, List

from lyra.engine.interpreter import Interpreter
from lyra.engine.result import AnalysisResult
from lyra.semantics.forward import ForwardSemantics

from lyra.abstract_domains.state import State
from lyra.core.cfg import Basic, Loop, Conditional, Edge, Node, ControlFlowGraph


class ForwardInterpreter(Interpreter):
    """Forward control flow graph interpreter."""

    def __init__(self, cfgs, fargs, semantics: ForwardSemantics, widening, precursory=None):
        """Forward control flow graph interpreter construction.

        :param cfgs: control flow graphs to analyze
        :param fargs: formal arguments of functions
        :param semantics: semantics of statements in the control flow graph
        :param widening: number of iterations before widening
        :param precursory: precursory control flow graph interpreter
        """
        super().__init__(cfgs, fargs, semantics, widening, precursory)

    def analyze(self, cfg: ControlFlowGraph, initial: State) -> AnalysisResult:
        from lyra.engine.backward import BackwardInterpreter

        context: State = deepcopy(initial)

        # run the precursory analysis (if any)
        if self.precursory:  # there is a precursory analysis to be run
            pre_result: Optional[AnalysisResult] = self.precursory.analyze(cfg, initial.precursory)
        else:  # there is no precursory analysis to be run
            pre_result: Optional[AnalysisResult] = None

        # prepare the worklist and iteration counts
        worklist = Queue()
        worklist.put(cfg.in_node)
        iterations = {node: 0 for node in cfg.nodes}

        while not worklist.empty():
            current: Node = worklist.get()  # retrieve the current node

            iteration = iterations[current.identifier]

            # retrieve the previous entry state of the node
            try:
                previous = deepcopy(self.result.get_node_result(current)[context][0])
            except:
                previous = None

            # compute the current entry state of the current node
            entry = deepcopy(initial)
            if current.identifier != cfg.in_node.identifier:
                entry.bottom()
                # join incoming states
                edges = cfg.in_edges(current)
                for edge in edges:
                    if edge.source in self.result.result:
                        ctx = context
                        predecessor = deepcopy(self.result.get_node_result(edge.source)[ctx][-1])
                    else:
                        predecessor = deepcopy(initial).bottom()
                    # handle conditional edges
                    if isinstance(edge, Conditional) and edge.kind == Edge.Kind.DEFAULT:
                        neighbors = cfg.out_edges(edge.source)
                        branch = any(edge.kind == Edge.Kind.IF_IN for edge in neighbors)
                        loop = any(edge.kind == Edge.Kind.LOOP_IN for edge in neighbors)
                        assert (branch or loop) and not (branch and loop)
                        predecessor = predecessor.enter_if() if branch else predecessor
                        predecessor = predecessor.enter_loop() if loop else predecessor
                        condition = edge.condition

                        if pre_result:  # a precursory analysis was run
                            if isinstance(self.precursory, BackwardInterpreter):
                                ctx = context.precursory
                                precursory = pre_result.get_node_result(edge.target)[ctx][0]
                            else:
                                assert isinstance(self.precursory, ForwardInterpreter)
                                ctx = context.precursory
                                precursory = pre_result.get_node_result(edge.source)[ctx][-1]
                        else:           # no precursory analysis was run
                            precursory = None

                        predecessor = predecessor.before(condition.pp, precursory)
                        predecessor = self.semantics.semantics(condition, predecessor, self)
                        predecessor = predecessor.filter()
                        predecessor = predecessor.exit_if() if branch else predecessor
                        predecessor = predecessor.exit_loop() if loop else predecessor
                    elif edge.kind == Edge.Kind.IF_IN:
                        predecessor = predecessor.enter_if()
                        assert isinstance(edge, Conditional)
                        condition = edge.condition

                        if pre_result:  # a precursory analysis was run
                            if isinstance(self.precursory, BackwardInterpreter):
                                ctx = context.precursory
                                precursory = pre_result.get_node_result(edge.target)[ctx][0]
                            else:
                                assert isinstance(self.precursory, ForwardInterpreter)
                                ctx = context.precursory
                                precursory = pre_result.get_node_result(edge.source)[ctx][-1]
                        else:           # no precursory analysis was run
                            precursory = None

                        predecessor = predecessor.before(condition.pp, precursory)
                        predecessor = self.semantics.semantics(condition, predecessor, self)
                        predecessor = predecessor.filter()
                    elif edge.kind == Edge.Kind.LOOP_IN:
                        predecessor = predecessor.enter_loop()
                        assert isinstance(edge, Conditional)
                        condition = edge.condition

                        if pre_result:  # a precursory analysis was run
                            if isinstance(self.precursory, BackwardInterpreter):
                                ctx = context.precursory
                                precursory = pre_result.get_node_result(edge.target)[ctx][0]
                            else:
                                assert isinstance(self.precursory, ForwardInterpreter)
                                ctx = context.precursory
                                precursory = pre_result.get_node_result(edge.source)[ctx][-1]
                        else:           # no precursory analysis was run
                            precursory = None

                        predecessor = predecessor.before(condition.pp, precursory)
                        predecessor = self.semantics.semantics(condition, predecessor, self)
                        predecessor = predecessor.filter()
                    # handle unconditional non-default edges
                    if edge.kind == Edge.Kind.IF_OUT:
                        predecessor = predecessor.exit_if()
                    elif edge.kind == Edge.Kind.LOOP_OUT:
                        predecessor = predecessor.exit_loop()
                    entry = entry.join(predecessor)
                # widening
                if isinstance(current, Loop) and self.widening < iteration:
                    entry = deepcopy(previous).widening(entry)

            # check for termination and execute block
            if previous is None or not entry.less_equal(previous):
                states = deque([entry])
                if isinstance(current, Basic):
                    successor = entry

                    if pre_result:     # a precursory analysis was run
                        ctx = context.precursory
                        pre_states = pre_result.get_node_result(current)[ctx]
                        if isinstance(self.precursory, BackwardInterpreter):
                            pre_states = pre_states[1:]
                        else:
                            assert isinstance(self.precursory, ForwardInterpreter)
                            pre_states = pre_states[:-1]
                    else:              # no precursory analysis was run
                        pre_states: List[Optional[State]] = [None] * len(current.stmts)

                    for precursory, stmt in zip(pre_states, current.stmts):
                        successor = successor.before(stmt.pp, precursory)
                        successor = self.semantics.semantics(stmt, deepcopy(successor), self)
                        states.append(successor)
                elif isinstance(current, Loop):
                    # nothing to be done
                    pass
                self.result.set_node_result(current, context, list(states))
                # update worklist and iteration count
                for node in cfg.successors(current):
                    worklist.put(node)
                iterations[current.identifier] = iteration + 1

        # print(states)
        return self.result
