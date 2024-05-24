from typing import Callable, Set, Dict, Any
from multilevel_graphs.contraction_schemes import ContractionScheme, ComponentSet, DecTable
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge, maximal_cliques


class CliquesContractionScheme(ContractionScheme):
    def __init__(self, level: int,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None,
                 reciprocal: bool = False):
        """
            Initializes a contraction scheme based on the contraction function by cliques.
            In a decontractible (directed) graph, a clique is a subset of nodes of a graph such that every two distinct
            nodes are adjacent.
            A maximal clique is a clique that is not a subset of any other clique.
            The reciprocal parameter determines how two nodes are considered adjacent: if True, two nodes are adjacent if
            there is an edge between them in both directions in the original graph, otherwise, two nodes are adjacent if
            there is an edge between them in at least one direction in the original graph.

            :param level: the level of the contraction scheme in the multilevel graph where this scheme resides
            :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
            :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
            :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
            :param reciprocal: if True, two nodes are considered adjacent if there is an edge between them in both directions
        """
        super().__init__(level, supernode_attr_function, superedge_attr_function, c_set_attr_function)
        self._reciprocal = reciprocal

    @property
    def contraction_name(self) -> str:
        return "cliques_" + ("" if self._reciprocal else "not_") + "rec"

    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        cliques = maximal_cliques(dec_graph, self._reciprocal)

        return DecTable([ComponentSet(self._get_component_set_id(),
                                      clique,
                                      **(self._c_sets_attr_function(clique))) for clique in cliques])
