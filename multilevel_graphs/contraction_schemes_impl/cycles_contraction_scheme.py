from typing import Callable, Set, Dict, Any

from multilevel_graphs.contraction_schemes import ContractionScheme, DecTable, ComponentSet
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge, simple_cycles


class CyclesContractionScheme(ContractionScheme):
    maximal: bool

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

    @property
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
                                      **(self._c_set_attr_function(cycle))) for cycle in cycles])

    def _update_added_node(self, supernode: Supernode):
        self.contraction_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                         {supernode},
                                                         **(self._c_set_attr_function({supernode}))))

        key_component_set = frozenset(self.contraction_sets_table[supernode])

        new_supernode = Supernode(self._get_supernode_id(),
                                  level=self.level,
                                  contraction_sets=key_component_set,
                                  **(self._supernode_attr_function(supernode)))
        new_supernode.add_node(supernode)

        self.supernode_table[key_component_set] = new_supernode
        supernode.supernode = new_supernode

    def _update_removed_node(self, supernode: Supernode):
        # TODO: Implement this method
        pass

    def _update_added_edge(self, superedge: Superedge):
        # TODO: Implement this method
        pass

    def _update_removed_edge(self, superedge: Superedge):
        # TODO: Implement this method
        pass
