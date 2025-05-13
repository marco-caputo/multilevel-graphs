from typing import Callable, Set, Dict, Any, List, Optional, Tuple
from src.multilevelgraphs.contraction_schemes import DecontractionEdgeBasedContractionScheme, ComponentSet, CompTable
from src.multilevelgraphs.dec_graphs import DecGraph, Supernode, Superedge


class StarsContractionScheme(DecontractionEdgeBasedContractionScheme):
    """
    An edge-based contraction scheme based on the contraction function by stars.
    According to this scheme, two nodes are in the same component set if they share the same node as their only
    adjacent node or if the node has this role for some other node.
    In this scheme there is a one-to-one correspondence between supernodes and component sets.

    In a decontractible (directed) graph, a star is a complete bipartite graph with sets of cardinality
    1 and k >= 0. In this scheme, a star is a subset of such set of nodes, which doesn't include nodes
    adjacent to some other nodes outside the center node of the star.

    The reciprocal attribute of the scheme determines how two nodes are considered adjacent: if True, two nodes are
    adjacent if there is an edge between them in both directions in the original graph, otherwise, two nodes are
    adjacent if there is an edge between them in at least one direction in the original graph.

    Attributes
    ----------
    _reciprocal : bool
        boolean value that determines how two nodes are considered adjacent in the original graph
    """
    _reciprocal: bool

    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None,
                 reciprocal: bool = False):
        """
            Initializes a contraction scheme based on the contraction function by stars.
            In a decontractible (directed) graph, a star is a complete bipartite graph with sets of cardinality
            1 and k. In this scheme, a star is a subset of such set of nodes, which doesn't include nodes
            adjacent to some other nodes outside the center node of the star.

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
        return "stars_" + ("" if self._reciprocal else "not_") + "rec"

    def clone(self):
        return StarsContractionScheme(self._supernode_attr_function,
                                      self._superedge_attr_function,
                                      self._c_set_attr_function,
                                      self._reciprocal)

    def contraction_function(self, dec_graph: DecGraph) -> CompTable:
        stars = self._star_sets(dec_graph)
        comp_table = CompTable([ComponentSet(self._get_component_set_id(),
                                             star,
                                             **(self._c_set_attr_function(star))) for star in stars])

        for node in dec_graph.V.values():
            if node not in comp_table:
                comp_table.add_set(ComponentSet(self._get_component_set_id(),
                                                {node},
                                                **(self._c_set_attr_function({node}))))

        comp_table.modified.clear()

        return comp_table

    def _star_sets(self, dec_graph: DecGraph) -> List[Set[Supernode]]:
        """
        Returns the list of stars of supernodes in the decontracted graph of this scheme.
        A star is a set of supernodes where each supernode has the same only one adjacent supernode in the
        decontracted graph, plus that node itself at the center of the star.
        If a node is not part of any star, it is not added to the result as a singleton.

        :param dec_graph: the decontracted graph
        :return: the list of star sets
        """
        # Dictionary mapping supernodes at the center of a star with their corresponding star set
        star_dict: Dict[Supernode, Set[Supernode]] = dict()
        for supernode in dec_graph.V.values():
            _, adj_node = self._adjacent_nodes(supernode, dec_graph)
            if adj_node is not None and supernode not in star_dict:
                star_dict.setdefault(adj_node, {adj_node}).add(supernode)

        return list(star_dict.values())

    def _adjacent_nodes(self, supernode: Supernode, dec_graph: DecGraph) -> Tuple[int, Optional[Supernode]]:
        """
        Returns the number of adjacent supernodes of the given supernode in the given decontracted graph according to
        the reciprocal parameter of this scheme, along with the only adjacent supernode as the second return value,
        if such supernode exists.
        If more than one or no nodes are adjacent to the given supernode, None is returned as second return value.

        :param supernode: the supernode
        :param dec_graph: the decontracted graph
        :return: the number of adjacent nodes and the only adjacent supernode, if any
        """
        adj_nodes = ({e.tail for e in dec_graph.in_edges(supernode)} &
                     {e.head for e in dec_graph.out_edges(supernode)}) \
            if self._reciprocal else \
            ({e.tail for e in dec_graph.in_edges(supernode)} |
             {e.head for e in dec_graph.out_edges(supernode)})

        return len(adj_nodes), adj_nodes.pop() if len(adj_nodes) == 1 else None

    def _update_added_edge(self, edge: Superedge):
        self.set_decontracted_graph()

        a, b = edge.tail, edge.head
        prev_adj = dict()
        prev_adj[a] = self._adjacent_nodes(a, self._decontracted_graph)
        prev_adj[b] = self._adjacent_nodes(b, self._decontracted_graph)

        if a.supernode == b.supernode:
            a.supernode.add_edge(edge)
        else:
            self._add_edge_in_superedge(a.supernode.key, b.supernode.key, edge)

        self._add_edge_to_decontraction(edge)
        current_adj = dict()
        current_adj[a] = self._adjacent_nodes(a, self._decontracted_graph)
        current_adj[b] = self._adjacent_nodes(b, self._decontracted_graph)

        # Nodes are ordered by the number of adjacent nodes in the decontracted graph in descending order
        if prev_adj[a][0] < prev_adj[b][0]:
             a, b = b, a

        for node in [a, b]:
            if prev_adj[node][0] == 1 and current_adj[node][0] != 1:
                # If the node was not part of a two-nodes star
                if self._adjacent_nodes(prev_adj[node][1], self._decontracted_graph)[0] != 1:
                    set_to_split = next(iter(self.component_sets_table[node]))
                    self.component_sets_table.remove_set(set_to_split)
                    self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                   {node},
                                                                   **(self._c_set_attr_function({node}))))
                    self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                   set_to_split - {node},
                                                                   **(self._c_set_attr_function(set_to_split - {node})))
                                                      )

            elif prev_adj[node][0] == 0 and current_adj[node][0] != 0:
                singleton_set = next(iter(self.component_sets_table[node]))
                self.component_sets_table.remove_set(singleton_set)
                other_node = b if node == a else a
                other_set = next(iter(self.component_sets_table[other_node]))
                self.component_sets_table.remove_set(other_set)
                self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                               other_set | {node},
                                                               **(self._c_set_attr_function(other_set | {node})))
                                                  )
                break

    def _update_removed_edge(self, edge: Superedge):
        self.set_decontracted_graph()

        a, b = edge.tail, edge.head
        prev_adj = dict()
        prev_adj[a] = self._adjacent_nodes(a, self._decontracted_graph)
        prev_adj[b] = self._adjacent_nodes(b, self._decontracted_graph)

        if a.supernode == b.supernode:
            a.supernode.remove_edge(edge)
        else:
            self._remove_edge_in_superedge(a.supernode.key, b.supernode.key, edge)

        self._remove_edge_from_decontraction(edge)
        current_adj = dict()
        current_adj[a] = self._adjacent_nodes(a, self._decontracted_graph)
        current_adj[b] = self._adjacent_nodes(b, self._decontracted_graph)

        # Nodes are ordered by the number of adjacent nodes in the decontracted graph in ascending order
        if prev_adj[a][0] > prev_adj[b][0]:
            a, b = b, a

        for node in [a, b]:
            if prev_adj[node][0] > 1 and current_adj[node][0] == 1:
                # If the node is now not part of a two-nodes star
                if self._adjacent_nodes(current_adj[node][1], self._decontracted_graph)[0] != 1:
                    singleton_set = next(iter(self.component_sets_table[node]))
                    self.component_sets_table.remove_set(singleton_set)
                    adj_node_set = next(iter(self.component_sets_table[current_adj[node][1]]))
                    self.component_sets_table.remove_set(adj_node_set)
                    self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                                   adj_node_set | {node},
                                                                   **(self._c_set_attr_function(adj_node_set | {node})))
                                                      )

            elif prev_adj[node][0] == 1 and current_adj[node][0] == 0:
                set_to_split = next(iter(self.component_sets_table[node]))
                self.component_sets_table.remove_set(set_to_split)
                self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                               {node},
                                                               **(self._c_set_attr_function({node}))))
                self.component_sets_table.add_set(ComponentSet(self._get_component_set_id(),
                                                               set_to_split - {node},
                                                               **(self._c_set_attr_function(set_to_split - {node})))
                                                  )
                other_node = b if node == a else a
                if prev_adj[other_node][0] == 1 and current_adj[other_node][0] == 0:
                    break
