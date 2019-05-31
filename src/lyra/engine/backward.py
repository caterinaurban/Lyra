"""
Backward Analysis Engine
========================

:Author: Caterina Urban
"""

from collections import deque
from copy import deepcopy
from queue import Queue
from typing import List, Optional

from lyra.engine.interpreter import Interpreter
from lyra.engine.result import AnalysisResult
from lyra.semantics.backward import BackwardSemantics

from lyra.abstract_domains.state import State
from lyra.core.cfg import Basic, Loop, Conditional, Edge, Node


class BackwardInterpreter(Interpreter):
    """Backward control flow graph interpreter."""

    def __init__(self, cfg, semantics: BackwardSemantics, widening, precursory=None):
        """Backward control flow graph interpreter construction.

        :param cfg: control flow graph to analyze
        :param semantics: semantics of statements in the control flow graph
        :param widening: number of iterations before widening
        :param precursory: precursory control flow graph interpreter
        """
        super().__init__(cfg, semantics, widening, precursory)

    @property
    def semantics(self):
        return self._semantics

    def analyze(self, initial: State) -> AnalysisResult:
        from lyra.engine.forward import ForwardInterpreter

        # run the precursory analysis (if any)
        if self.precursory:     # there is a precursory analysis to be run
            pre_result: Optional[AnalysisResult] = self.precursory.analyze(initial.precursory)
        else:                   # there is no precursory analysis to be run
            pre_result: Optional[AnalysisResult] = None

        # prepare the worklist and iteration counts
        worklist = Queue()
        worklist.put(self.cfg.out_node)
        iterations = {node: 0 for node in self.cfg.nodes}
        done = set()

        while not worklist.empty():
            current: Node = worklist.get()  # retrieve the current node

            iteration = iterations[current.identifier]

            # retrieve the previous exit state of the node
            if current in self.result.result:
                previous = deepcopy(self.result.get_node_result(current)[-1])
            else:
                previous = None

            # compute the current exit state of the current node
            entry = deepcopy(initial)
            if current.identifier != self.cfg.out_node.identifier:
                entry.bottom()
                # join incoming states
                edges = self.cfg.out_edges(current)
                for edge in edges:
                    if edge.target in self.result.result:
                        successor = deepcopy(self.result.get_node_result(edge.target)[0])
                    else:
                        successor = deepcopy(initial).bottom()
                    # handle unconditional non-default edges
                    if edge.kind == Edge.Kind.IF_OUT:
                        successor = successor.enter_if()
                    elif edge.kind == Edge.Kind.LOOP_OUT:
                        successor = successor.enter_loop()
                    # handle conditional edges
                    if isinstance(edge, Conditional) and edge.kind == Edge.Kind.DEFAULT:
                        branch = any(edge.kind == Edge.Kind.IF_IN for edge in edges)
                        loop = any(edge.kind == Edge.Kind.LOOP_IN for edge in edges)
                        assert (branch or loop) and not (branch and loop)
                        successor = successor.enter_if() if branch else successor
                        successor = successor.enter_loop() if loop else successor

                        if pre_result:  # a precursory analysis was run
                            if isinstance(self.precursory, ForwardInterpreter):
                                precursory = pre_result.get_node_result(edge.source)[-1]
                            else:
                                assert isinstance(self.precursory, BackwardInterpreter)
                                precursory = pre_result.get_node_result(edge.target)[0]
                        else:           # no precursory analysis was run
                            precursory = None

                        successor = successor.before(edge.condition.pp, precursory)
                        successor = self.semantics.semantics(edge.condition, successor)
                        successor = successor.filter(bwd=True)
                        successor = successor.exit_if() if branch else successor
                        successor = successor.exit_loop() if loop else successor
                    elif edge.kind == Edge.Kind.IF_IN:
                        assert isinstance(edge, Conditional)

                        if pre_result:  # a precursory analysis was run
                            if isinstance(self.precursory, ForwardInterpreter):
                                precursory = pre_result.get_node_result(edge.source)[-1]
                            else:
                                assert isinstance(self.precursory, BackwardInterpreter)
                                precursory = pre_result.get_node_result(edge.target)[0]
                        else:           # no precursory analysis was run
                            precursory = None

                        successor = successor.before(edge.condition.pp, precursory)
                        successor = self.semantics.semantics(edge.condition, successor)
                        successor = successor.filter(bwd=True)
                        successor = successor.exit_if()
                    elif edge.kind == Edge.Kind.LOOP_IN:
                        assert isinstance(edge, Conditional)

                        if pre_result:  # a precursory analysis was run
                            if isinstance(self.precursory, ForwardInterpreter):
                                precursory = pre_result.get_node_result(edge.source)[-1]
                            else:
                                assert isinstance(self.precursory, BackwardInterpreter)
                                precursory = pre_result.get_node_result(edge.target)[0]
                        else:           # no precursory analysis was run
                            precursory = None

                        successor = successor.before(edge.condition.pp, precursory)
                        successor = self.semantics.semantics(edge.condition, successor)
                        successor = successor.filter(bwd=True)
                        successor = successor.exit_loop()
                    entry = entry.join(successor)
                # widening
                if isinstance(current, Loop) and self.widening < iteration:
                    entry = deepcopy(previous).widening(entry)

            # check for termination and execute block
            if previous is None or not entry.less_equal(previous):
                states = deque([entry])
                if isinstance(current, Basic):
                    successor = entry

                    if pre_result:     # a precursory analysis was run
                        pre_states: List[Optional[State]] = pre_result.get_node_result(current)
                        if isinstance(self.precursory, ForwardInterpreter):
                            pre_states = pre_states[:-1]
                        else:
                            assert isinstance(self.precursory, BackwardInterpreter)
                            pre_states = pre_states[1:]
                    else:              # no precursory analysis was run
                        pre_states: List[Optional[State]] = [None] * len(current.stmts)

                    for precursory, stmt in zip(reversed(pre_states), reversed(current.stmts)):
                        successor = successor.before(stmt.pp, precursory)
                        successor = self.semantics.semantics(stmt, deepcopy(successor))
                        states.appendleft(successor)
                elif isinstance(current, Loop):
                    # nothing to be done
                    pass
                self.result.set_node_result(current, list(states))
                # update worklist and iteration count
                for node in self.cfg.predecessors(current):
                    worklist.put(node)
                iterations[current.identifier] = iteration + 1

        return self.result
