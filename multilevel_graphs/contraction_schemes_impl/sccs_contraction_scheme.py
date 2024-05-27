from typing import Callable, Dict, Any, Set
import networkx as nx

from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import ContractionScheme, DecTable, ComponentSet
from multilevel_graphs.dec_graphs.algorithms import strongly_connected_components


class SccsContractionScheme(ContractionScheme):
    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None):
        """
        Initializes a contraction scheme based on the contraction function by strongly connected components.
        A strongly connected component (SCC) of a decontractible (directed) graph is a maximal subgraph in which
        there is a path between every pair of nodes.

        For this contraction scheme, there is a one-to-one correspondence between the strongly connected components
        of the decontractible graph and the component sets of the contraction scheme.

        :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
        :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
        :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
        """
        super().__init__(supernode_attr_function, superedge_attr_function, c_set_attr_function)

    @property
    def contraction_name(self) -> str:
        return "scc"

    def clone(self):
        return SccsContractionScheme(self._supernode_attr_function,
                                     self._superedge_attr_function,
                                     self._c_set_attr_function)

    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        sccs = strongly_connected_components(dec_graph)
        return DecTable([ComponentSet(self._get_component_set_id(),
                                      scc,
                                      **(self._c_set_attr_function(scc))) for scc in sccs])

    def _update_added_edge(self, edge: Superedge):
        # TODO: Implement this method
        pass

    def _update_removed_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode

        if u != v:
            self._remove_edge_in_superedge(u, v, edge)
        else:
            u.remove_edge(edge)
            inner_reachable_nodes = self._reachable_nodes_from(u.dec, edge.tail)
            if inner_reachable_nodes != u.dec.nodes():
                h = u.dec.induced_subgraph(u.dec.nodes() - inner_reachable_nodes)
                sccs_in_h = strongly_connected_components(h)

                self.contraction_sets_table.remove_set(next(iter(u.component_sets)))
                self.contraction_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                 inner_reachable_nodes,
                                                                 **(self._c_set_attr_function(h.nodes()))))
                for scc in sccs_in_h:
                    self.contraction_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                     scc,
                                                                     **(self._c_set_attr_function(scc))))

    @staticmethod
    def _reachable_nodes_from(dec_graph: DecGraph, node: Supernode) -> Set[Supernode]:
        descendants = nx.descendants(dec_graph.graph(), node.key)
        return {dec_graph.V[key] for key in descendants}
