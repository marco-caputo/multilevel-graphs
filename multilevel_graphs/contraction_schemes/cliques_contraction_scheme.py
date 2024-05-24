from typing import Callable, Set, Dict, Any
from multilevel_graphs.contraction_schemes import ContractionScheme, ComponentSet, DecTable
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge, enumerate_all_cliques


class CliquesContractionScheme(ContractionScheme):
    def __init__(self, level: int,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None,
                 reciprocal: bool = False):
        super().__init__(level, supernode_attr_function, superedge_attr_function, c_set_attr_function)
        self._reciprocal = reciprocal

    @property
    def contraction_name(self) -> str:
        return "cliques_" + ("" if self._reciprocal else "not_") + "rec"

    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        cliques = enumerate_all_cliques(dec_graph, self._reciprocal)

        return DecTable([ComponentSet(self._get_component_set_id(),
                                      clique,
                                      **(self._c_sets_attr_function(clique))) for clique in cliques])
