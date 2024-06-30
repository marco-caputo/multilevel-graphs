from typing import Callable, Set, Dict, Any, List, Optional, Generator, Iterator, Tuple
import networkx as nx

from multilevelgraphs.contraction_schemes import EdgeBasedContractionScheme, CompTable, ComponentSet
from multilevelgraphs.dec_graphs import DecGraph, Supernode, Superedge, simple_cycles


class CyclesContractionScheme(EdgeBasedContractionScheme):
    """
    A contraction scheme based on the contraction function by simple cycles.
    According to this scheme, two nodes are in the same component set if they are part of the same simple cycle among
    all distinct simple cycles in the graph, and two nodes are part of the same supernode if they are part of the same
    set of simple cycles.
    In this scheme there is a one-to-one correspondence between supernodes and distinct non-empty sets of component
    sets.

    In a decontractible (directed) graph, a simple cycle, or elementary circuit, is a closed path where no node
    appears twice.
    Two simple cycles are distinct if they are not cyclic permutations of each other.
    A maximal simple cycle is a simple cycle that is not a subset of any other simple cycle.

    The maximal attribute of the scheme determines whether only maximal simple cycles are considered.

    Attributes
    ----------
    _maximal : bool
        boolean value that determines whether only maximal simple cycles are considered
    """
    _maximal: bool
    _decontracted_graph: Optional[DecGraph]

    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None,
                 maximal: bool = True):
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
        return "simple" + ("_maximal" if self._maximal else "") + "_cycles"

    def clone(self):
        return CyclesContractionScheme(self._supernode_attr_function,
                                       self._superedge_attr_function,
                                       self._c_set_attr_function,
                                       self._maximal)

    def contraction_function(self, dec_graph: DecGraph) -> CompTable:
        comp_sets = self._component_set_from_cycles(simple_cycles(dec_graph))

        if self._maximal:
            comp_table = CompTable(maximal=self._maximal)
            for c_set in sorted(list(comp_sets), key=lambda c_set: len(c_set), reverse=True):
                comp_table.add_maximal_set(c_set, check_subsets=False)

        else:
            comp_table = CompTable(comp_sets, maximal=self._maximal)

        for node in dec_graph.V.values():
            if node not in comp_table:
                comp_table.add_set(ComponentSet(self._get_component_set_id(),
                                                {node},
                                                **(self._c_set_attr_function({node}))))

        comp_table.modified.clear()

        return comp_table

    def _component_set_from_cycles(self, cycles: Generator[Tuple[Supernode, ...], None, None]) -> Generator[ComponentSet, None, None]:
        for cycle in cycles:
            cycle_set = set(cycle)
            yield ComponentSet(self._get_component_set_id(), cycle_set, **(self._c_set_attr_function(cycle_set)))

    def _update_added_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode

        if u == v:
            u.add_edge(edge)
        else:
            self._add_edge_in_superedge(u.key, v.key, edge)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.add_edge(Superedge(edge.tail, edge.head))

        # Find all the simple cycles that contain the new edge and track them in the component sets table
        for new_circuit in self.cycle_search(self._decontracted_graph.graph(), [edge.tail.key, edge.head.key]):
            new_c_set = ComponentSet(self._get_component_set_id(),
                                     {self._decontracted_graph.V[node] for node in new_circuit})
            self.component_sets_table.add_set(new_c_set, maximal=self._maximal)

    def _update_removed_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode

        if u == v:
            u.remove_edge(edge)
        else:
            self._remove_edge_in_superedge(u.key, v.key, edge)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.remove_edge(Superedge(edge.tail, edge.head))

        c_sets_intersection = \
            set.intersection(self.component_sets_table[edge.tail], self.component_sets_table[edge.head])

        for c_set in c_sets_intersection:
            # We look for possible alternative cycles that contain all nodes in c_set
            c_set_keys = frozenset({n.key for n in c_set})
            cycles_in_c_set_with_tail = {frozenset(cycle) for cycle in
                                         self.cycle_search(self._decontracted_graph.graph().subgraph(c_set_keys),
                                                           [edge.tail.key])}
            if c_set_keys not in cycles_in_c_set_with_tail:
                self.component_sets_table.remove_set(c_set)

                # If the scheme is maximal, new maximal cycles that are sub-cycles of the removed cycle are considered.
                # If not, the sub-cycles must be already tracked in the table.
                if self._maximal:
                    for cycle in cycles_in_c_set_with_tail:
                        self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                       {self._decontracted_graph.V[key] for key in
                                                                        cycle}),
                                                          maximal=True)

                    # All remaining cycles in c_set that does not contain edge.tail must be considered
                    remaining_cycles_in_c_set = [
                        {self._decontracted_graph.V[key] for key in cycle} for cycle in
                        nx.simple_cycles(self._decontracted_graph.graph().subgraph(c_set_keys - {edge.tail.key}))
                    ]
                    for cycle in remaining_cycles_in_c_set:
                        self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(), cycle),
                                                          maximal=True)
        # Some nodes may no longer be part of any cycle
        self.component_sets_table.add_singletons(self._get_component_set_id)

    # The following methods are overridden to update the decontracted graph used during the other update
    # procedures of the scheme.
    def _update_added_node(self, node: Supernode):
        super()._update_added_node(node)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.add_node(node)

    def _update_removed_node(self, node: Supernode):
        super()._update_removed_node(node)

        if not self._decontracted_graph:
            self._decontracted_graph = self.dec_graph.complete_decontraction()
        else:
            self._decontracted_graph.remove_node(node)

    @staticmethod
    def cycle_search(graph: nx.Graph, path: list) -> Generator:
        return nx.algorithms.cycles._johnson_cycle_search(graph, path)
