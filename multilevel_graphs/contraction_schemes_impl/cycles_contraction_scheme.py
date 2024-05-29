from typing import Callable, Set, Dict, Any, List, Optional
import networkx as nx
from networkx.algorithms.cycles import _johnson_cycle_search as cycle_search

from multilevel_graphs.contraction_schemes import EdgeBasedContractionScheme, DecTable, ComponentSet
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge, simple_cycles


class CyclesContractionScheme(EdgeBasedContractionScheme):
    maximal: bool
    _decontracted_graph: Optional[nx.DiGraph]

    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None,
                 maximal: bool = False):
        """
        Initializes a contraction scheme based on the contraction function by simple cycles.
        A simple cycle, or elementary circuit, is a closed path where no node appears twice.
        In a decontractible (directed) graph, two simple cycles are distinct if they are not cyclic permutations of
        each other.
        A maximal simple cycle is a simple cycle that is not a subset of any other simple cycle.

        :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
        :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
        :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
        :param maximal: if True, only maximal simple cycles are considered
        """
        super().__init__(supernode_attr_function, superedge_attr_function, c_set_attr_function)
        self._maximal = maximal
        self._decontracted_graph = None  # Used to store the current complete decontraction during subsequent updates

    def contraction_name(self) -> str:
        return "simple_" + ("_maximal" if self._maximal else "") + "_cycles"

    def clone(self):
        return CyclesContractionScheme(self._supernode_attr_function,
                                       self._superedge_attr_function,
                                       self._c_set_attr_function,
                                       self._maximal)

    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        cycles = [set(cycle) for cycle in simple_cycles(dec_graph)]
        return DecTable([ComponentSet(self._get_component_set_id(),
                                      cycle,
                                      **(self._c_set_attr_function(cycle))) for cycle in cycles],
                        maximal=self._maximal)

    def _update_added_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode

        if u == v:
            u.add_edge(edge)
        else:
            self._add_edge_in_superedge(u.key, v.key, edge)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction().graph()
        else:
            self._decontracted_graph.add_edge(u.key, v.key)

        # Find all the simple cycles that contain the new edge and track them in the component sets table
        for new_circuit in cycle_search(self._decontracted_graph, [edge.tail.key, edge.head.key]):
            new_c_set = ComponentSet(self._get_component_set_id(), set(new_circuit))
            self.component_sets_table.add_set(new_c_set, maximal=self.maximal)

    def _update_removed_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode

        if u == v:
            u.remove_edge(edge)
        else:
            self._remove_edge_in_superedge(u.key, v.key, edge)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction().graph()
        else:
            self._decontracted_graph.remove_edge(u.key, v.key)

        c_sets_intersection = \
            set.intersection(self.component_sets_table[edge.tail], self.component_sets_table[edge.head])

        for c_set in c_sets_intersection:
            # We look for possible alternative cycles that contain all nodes in c_set
            cycles_in_c_set_with_tail = {frozenset(cycle) for cycle in
                                         cycle_search(self._decontracted_graph.subgraph(set(c_set)), [edge.tail.key])}
            if frozenset(c_set) not in cycles_in_c_set_with_tail:
                self.component_sets_table.remove_set(c_set)

                # If the scheme is maximal, new maximal cycles that are sub-cycles of the removed cycle are considered.
                # If not, the sub-cycles must be already tracked in the table.
                if self.maximal:
                    for cycle in cycles_in_c_set_with_tail:
                        self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(), set(cycle)),
                                                          maximal=True)

                    # All remaining cycles in c_set that does not contain edge.tail must be considered
                    remaining_cycles_in_c_set = [set(cycle) for cycle in nx.simple_cycles(
                        self._decontracted_graph.subgraph(c_set - {edge.tail.key}))]
                    for cycle in remaining_cycles_in_c_set:
                        self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(), cycle),
                                                          maximal=True)

    def _circuit_search(self, start: Any, end: Any, graph: nx.DiGraph, stack: List[Any]) -> List[List[Any]]:
        """
        Find all the circuits in the given graph that start and end at the given nodes.
        If the stack is not empty, finds all the circuits containing an edge between each node in the stack plus the
        given start node, in order.

        :param start: the start node
        :param end: the end node
        :param graph: the graph to search
        :param stack: the stack of nodes in the current path, prefix of the circuit
        :return: the list of circuits
        """

        pass
