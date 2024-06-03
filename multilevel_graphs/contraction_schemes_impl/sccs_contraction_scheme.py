from typing import Callable, Dict, Any, Set
import networkx as nx

from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import EdgeBasedContractionScheme, CompTable, ComponentSet
from multilevel_graphs.dec_graphs.algorithms import strongly_connected_components


class SccsContractionScheme(EdgeBasedContractionScheme):
    """
    A contraction scheme based on the contraction function by strongly connected components.
    According to this scheme, two nodes are in the same component set and supernode if they are part of the same
    strongly connected component in the decontractible graph.
    In this scheme there is a one-to-one correspondence between supernodes and component sets.

    A strongly connected component (SCC) of a decontractible (directed) graph is the node set of a maximal subgraph
    in which there is a path between every pair of nodes.
    """
    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None):
        """
        Initializes a contraction scheme based on the contraction function by strongly connected components.
        A strongly connected component (SCC) of a decontractible (directed) graph is the node set of a maximal subgraph
        in which there is a path between every pair of nodes.

        For this contraction scheme, there is a one-to-one correspondence between the strongly connected components
        of the decontractible graph and the component sets of the contraction scheme.

        :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
        :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
        :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
        """
        super().__init__(supernode_attr_function, superedge_attr_function, c_set_attr_function)

    def contraction_name(self) -> str:
        return "scc"

    def clone(self):
        return SccsContractionScheme(self._supernode_attr_function,
                                     self._superedge_attr_function,
                                     self._c_set_attr_function)

    def contraction_function(self, dec_graph: DecGraph) -> CompTable:
        sccs = strongly_connected_components(dec_graph)
        return CompTable([ComponentSet(self._get_component_set_id(),
                                       set(scc),
                                       **(self._c_set_attr_function(set(scc)))) for scc in sccs])

    def _update_added_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode

        if u == v:
            u.add_edge(edge)
        else:
            self._add_edge_in_superedge(u.key, v.key, edge)
            if len(self.dec_graph.E[(u.key, v.key)].dec) == 1:
                reach_supernodes = self._reach_visit(v, u)
                if reach_supernodes:
                    for node in reach_supernodes:
                        self.component_sets_table.remove_set(next(iter(node.component_sets)))
                    new_set = set.union(*[supernode.dec.nodes() for supernode in reach_supernodes])
                    self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                   new_set,
                                                                   **(self._c_set_attr_function(new_set))))
                    self._update_graph() # Updates graph structure for further updates

    def _reach_visit(self, start_node: Supernode, target_node: Supernode) -> Set[Supernode]:
        """
        Returns the set of supernodes in the decontractible graph of this contraction scheme that are both reachable
        from the start node and can reach the target node.

        :param start_node: the start supernode
        :param target_node: the target supernode
        :return: the set of supernodes that are both reachable from the start node and can reach the target node
        """
        can_reach_target_table = {target_node.key: True}
        self._reach_dfs(self.dec_graph.graph(), start_node.key, can_reach_target_table)
        return {self.dec_graph.V[node_key] for node_key, can_reach in can_reach_target_table.items() if can_reach}

    def _reach_dfs(self, graph: nx.DiGraph, u: Any, can_reach_target_table: Dict[Supernode, bool]):
        if u not in can_reach_target_table:
            can_reach_target_table[u] = False
            for v in graph.successors(u):
                self._reach_dfs(graph, v, can_reach_target_table)
                can_reach_target_table[u] |= can_reach_target_table[v]

    def _update_removed_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode

        if u != v:
            self._remove_edge_in_superedge(u.key, v.key, edge)
        else:
            u.remove_edge(edge)
            inner_reachable_nodes = self._reachable_nodes_from(u.dec, edge.tail)
            if inner_reachable_nodes != u.dec.nodes():
                h = u.dec.induced_subgraph(u.dec.nodes() - inner_reachable_nodes)
                sccs_in_h = strongly_connected_components(h)

                self.component_sets_table.remove_set(next(iter(u.component_sets)))
                self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                               inner_reachable_nodes,
                                                               **(self._c_set_attr_function(inner_reachable_nodes))))
                for scc in sccs_in_h:
                    self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                   set(scc),
                                                                   **(self._c_set_attr_function(set(scc)))))
                self._update_graph() # Updates graph structure for furthers updates

    @staticmethod
    def _reachable_nodes_from(dec_graph: DecGraph, node: Supernode) -> Set[Supernode]:
        descendants = nx.descendants(dec_graph.graph(), node.key)
        return {dec_graph.V[key] for key in descendants}.union({node})
