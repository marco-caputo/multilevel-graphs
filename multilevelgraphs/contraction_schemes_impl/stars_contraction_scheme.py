from typing import Callable, Set, Dict, Any, List, Optional
from multilevelgraphs.contraction_schemes import EdgeBasedContractionScheme, ComponentSet, CompTable
from multilevelgraphs.dec_graphs import DecGraph, Supernode, Superedge


class StarsContractionScheme(EdgeBasedContractionScheme):
    """
    An edge-based contraction scheme defined by the contraction function by stars.
    According to this scheme, two nodes are in the same component set if they share the same node as their only
    adjacent node or if the node has this role for some other node.
    In this scheme there is a one-to-one correspondence between supernodes and component sets.

    In a decontractible (directed) graph, a star is a complete bipartite graph with sets of cardinality
    1 and k. In this scheme, a star is a subset of such set of nodes, which doesn't consider nodes which
    are adjacent to some other nodes outside the center node of the star.

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
            1 and k. In this scheme, a star is a subset of such set of nodes, which doesn't consider nodes which
            are adjacent to some other nodes outside the center node of the star.

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
        # Dictionary of supernodes at the center of a star and the correspondent star set
        star_dict: Dict[Supernode, Set[Supernode]] = dict()
        for supernode in dec_graph.V.values():
            adj_node = self._adjacent_node(supernode, dec_graph)
            if adj_node and supernode not in star_dict:
                star_dict.setdefault(adj_node, {adj_node}).add(supernode)

        return list(star_dict.values())

    def _adjacent_node(self, supernode: Supernode, dec_graph: DecGraph) -> Optional[Supernode]:
        """
        Returns the only adjacent supernode of the given supernode in the decontracted graph according to the
        reciprocal parameter of this scheme.
        If more than one or no nodes are adjacent to the given supernode, None is returned.

        :param supernode: the supernode
        :param dec_graph: the decontracted graph
        :return: the adjacent supernode, if any
        """
        adj_nodes = ({e.tail for e in dec_graph.in_edges(supernode.key)} &
                     {e.head for e in dec_graph.out_edges(supernode.key)}) \
                if self._reciprocal else \
                    ({e.tail for e in dec_graph.in_edges(supernode.key)} |
                    {e.head for e in dec_graph.out_edges(supernode.key)})

        if len(adj_nodes) == 1:
            return adj_nodes.pop()

        return None

    def _update_added_edge(self, edge: Superedge):
        pass

    def _update_removed_edge(self, edge: Superedge):
        pass
