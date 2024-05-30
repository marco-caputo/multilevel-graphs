from typing import Callable, Set, Dict, Any
import networkx as nx
from multilevel_graphs.contraction_schemes import EdgeBasedContractionScheme, ComponentSet, DecTable
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge, maximal_cliques


class CliquesContractionScheme(EdgeBasedContractionScheme):
    reciprocal: bool

    def __init__(self,
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

            :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
            :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
            :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
            :param reciprocal: if True, two nodes are considered adjacent if there is an edge between them in both directions
        """
        super().__init__(supernode_attr_function, superedge_attr_function, c_set_attr_function)
        self._reciprocal = reciprocal

    def contraction_name(self) -> str:
        return "cliques_" + ("" if self._reciprocal else "not_") + "rec"

    def clone(self):
        return CliquesContractionScheme(self._supernode_attr_function,
                                        self._superedge_attr_function,
                                        self._c_set_attr_function,
                                        self._reciprocal)

    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        cliques = maximal_cliques(dec_graph, self._reciprocal)

        return DecTable([ComponentSet(self._get_component_set_id(),
                                      clique,
                                      **(self._c_set_attr_function(clique))) for clique in cliques])

    def _update_added_edge(self, edge: Superedge):
        u = edge.tail.supernode
        v = edge.head.supernode
        found_new_cliques = False

        if (v.key, u.key) in self.dec_graph.E and Superedge(u.key, v.key) in self.dec_graph.E[(v.key, u.key)]:
            undirected_clique_graph = self._undirected_clique_graph()
            supernodes_intersection = undirected_clique_graph.neighbors(u.key) & undirected_clique_graph.neighbors(v.key)

            # The union of nodes in each clique among neighbors of u and v, combined with the edge tail and head, is a
            # new clique at the lower level.
            intersection_cliques = [nx.find_cliques(undirected_clique_graph.subgraph(supernodes_intersection))]
            found_new_cliques = len(intersection_cliques) > 0
            for clique in intersection_cliques:
                self.component_sets_table.add_set(
                    ComponentSet(self._get_component_set_id(),
                                 set.union(*[self.dec_graph.V[key].dec.nodes() for key in clique]) | {edge.tail, edge.head})
                )

            # We look for cliques at the lower level to remove, as they are not maximal anymore.
            # Those are the cliques composed of the edge tail or head and nodes included in the decontractions of
            # supernodes in supernodes_intersection.
            if found_new_cliques:
                self._remove_collapsed_c_sets(supernodes_intersection, edge.tail)
                self._remove_collapsed_c_sets(supernodes_intersection, edge.head)

        if u != v:
            self._add_edge_in_superedge(u.key, v.key, edge)

        if found_new_cliques:
            self._update_graph()

    def _undirected_clique_graph(self) -> nx.Graph:
        """
        Returns the undirected graph of cliques of this scheme according to its reciprocal attribute.
        Un undirected graph of cliques is a graph where each node represents a (non necessarily maximal) clique of the
        decontracted graph, and two supernodes are adjacent if and only if each node in one supernode decontraction is
        adjacent to each node of the other supernode decontraction and, thus, the union of nodes in the two supernodes
        is also a clique.

        The notion of adjacency between two supernodes is determined by the reciprocal attribute of this scheme.

        :return: the undirected graph of cliques
        """
        undirected_version = self.dec_graph.graph().to_undirected(reciprocal=self._reciprocal)
        for und_edge in undirected_version.edges():
            if not self._are_superndoes_adjacent(*und_edge):
                undirected_version.remove_edge(*und_edge)
        return undirected_version

    def _are_superndoes_adjacent(self, u_key: Any, v_key: Any) -> bool:
        """
        Returns True if the supernodes u and v are adjacent in the decontracted graph of this scheme, False otherwise.
        The notion of adjacency between two supernodes is determined by the reciprocal attribute of this scheme,
        in particular:

        - If the reciprocal attribute is True, two supernodes are adjacent if there is a "complete" superedge between
        them in both directions, where a complete superedge is a superedge that has the maximum number of sub-edges,
        i.e., one sub-edge for each pair of nodes (a, b) where a is in the supernode of the tail and b is in
        the supernode of the head.

        - If the reciprocal attribute is False, two supernodes are adjacent if the union of the decontraction of the
        superedges between them contains at least one edge for each pair of nodes a, b in any direction (a, b) or (b, a)
        where a is in the supernode of the tail and b is in the supernode of the head.

        :param u: the first supernode
        :param v: the second supernode
        :return: True if the supernodes are adjacent, False otherwise
        """
        u = self.dec_graph.V[u_key]
        v = self.dec_graph.V[v_key]
        u_to_v = self.dec_graph.E[(u_key, v_key)] if (u_key, v_key) in self.dec_graph.E else None
        v_to_u = self.dec_graph.E[(v_key, u_key)] if (v_key, u_key) in self.dec_graph.E else None
        if self._reciprocal:
            return u_to_v is not None and v_to_u is not None and len(u_to_v)+len(v_to_u) == 2*len(u)*len(v)
        else:
            union_of_sub_edges = (set(u_to_v) if u_to_v is not None else set()) | \
                                 (set(v_to_u) if u_to_v is not None else set())
            return len({frozenset((edge.tail, edge.head)) for edge in union_of_sub_edges}) == len(u)*len(v)

    def _remove_collapsed_c_sets(self, supernodes_intersection: Set[Supernode], node: Supernode):
        """
        Removes all the non-maximal component sets in the table as a result of collapsing a clique into a new
        maximal clique.
        Those cliques to collapse are those which include the given node and nodes in the given supernodes intersection
        decontractions.

        :param supernodes_intersection: the intersection of the supernodes neighborhood
        :param node: the node that is part of the new maximal clique
        """
        # If we use update_graph after each change in the graph, it is not necessary to add:
        # - len(self._deleted_subnodes.get(node.supernode, set())
        if len(node.supernode) == 1:
            for c_set in self.component_sets_table[node]:
                if ({n.supernode for n in c_set} - {node}) <= supernodes_intersection:
                    self.component_sets_table.remove_set(c_set)
    def _update_removed_edge(self, edge: Superedge):
        # TODO: Implement this method
        pass