from typing import Callable, Set, Dict, Any

from multilevel_graphs.contraction_schemes import ContractionScheme, DecTable, ComponentSet
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge, simple_cycles


class CyclesContractionScheme(ContractionScheme):
    def __init__(self, level: int,
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

        :param level: the level of the contraction scheme in the multilevel graph where this scheme resides
        :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
        :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
        :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
        :param maximal: if True, only maximal simple cycles are considered
        """
        super().__init__(level, supernode_attr_function, superedge_attr_function, c_set_attr_function)
        self._maximal = maximal

    @property
    def contraction_name(self) -> str:
        return "simple_" + ("_maximal" if self._reciprocal else "") + "_cycles"

    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        cycles = simple_cycles(dec_graph)
        if self._maximal:
            cliques = {c for c in cycles if not any(c in c2 for c2 in cycles if c != c2)}
        return DecTable([ComponentSet(self._get_component_set_id(),
                                      clique,
                                      **(self._c_sets_attr_function(clique))) for clique in cliques])