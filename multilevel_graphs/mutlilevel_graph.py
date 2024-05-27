import networkx as nx
from typing import List, Optional, Any, Tuple
from multilevel_graphs import DecGraph, Supernode, Superedge, ContractionScheme
from multilevel_graphs.contraction_schemes import UpdateQuadruple


class MultilevelGraph:
    _dec_graph_0: DecGraph
    _contraction_schemes: List[ContractionScheme]

    def __init__(self, graph: nx.DiGraph, contraction_schemes: List[ContractionScheme] = None):
        """
        Initializes a multilevel graph based on the given NetworkX graph and list of contraction schemes.
        The multilevel graph definition is based on the contraction functions represented by the contraction
        schemes in the order of the given list.

        The multilevel graph is not immediately built from bottom to top at the initialization, but rather lazily
        constructed when the decontractible graph at a certain level is requested.

        :param graph: the NetworkX graph to be used as the base graph of the multilevel graph
        :param contraction_schemes: the list of contraction schemes to be used in the multilevel graph
        """
        self._dec_graph_0 = self.natural_transformation(graph)
        self._base_update_quadruple = UpdateQuadruple()
        self._contraction_schemes = [scheme.clone() for scheme in contraction_schemes] if contraction_schemes else []
        for i in range(self.height()):
            contraction_schemes[i].level = i + 1

    @staticmethod
    def natural_transformation(graph: nx.DiGraph) -> DecGraph:
        """
        Returns the natural transformation of the graph.
        The natural transformation of a graph is a decontractible graph such that:
        - each supernode has an empty decontractible graph as its decontraction
        - each superedge has an empty set of superedges as its decontraction
        - is isomorphic to the original graph
        The natural transformation produced by this method maintains keys and attributes of the nodes and edges
        of the original graph.
        """
        vs = dict(map(lambda c: (c[0], Supernode(c[0], **c[1])), graph.nodes(data=True)))
        es = dict(map(lambda t: ((t[0], t[1]), Superedge(vs[t[0]], vs[t[1]], **t[2])), graph.edges(data=True)))
        return DecGraph(vs, es)

    def build_contraction_schemes(self, upper_level: int = None):
        """
        Builds the contraction schemes of the multilevel graph from bottom to top, starting from the highest
        valid scheme in the hierarchy up to the given level.
        If no upper level is provided, the multilevel graph is fully updated, and further requests for a decontractible
        graph at a certain level will not require computation until the next modification of the multilevel graph.
        If the level provided is lower than the highest valid scheme, nothing happens.

        The involved contraction schemes in this multilevel graph hierarchy become valid and the corresponding
        decontractible graphs are reconstructed and replaced with new ones or are dynamically updated, based on
        the state of the highest-level valid scheme.
        """
        if upper_level is None or upper_level > self.height():
            upper_level = self.height()

        last_dec_graph, lower_level = self._highest_valid_graph()
        if lower_level >= upper_level:
            return

        for i in range(lower_level, upper_level):
            update_q = self._contraction_schemes[i - 1].update_quadruple if i > 1 else self._base_update_quadruple

            if self._contraction_schemes[i].dec_graph is None:
                last_dec_graph = self._contraction_schemes[i].contract(last_dec_graph)
            else:
                last_dec_graph = self._contraction_schemes[i].update(update_q)

            update_q.clear()

    def _highest_valid_graph(self) -> Tuple[DecGraph, int]:
        """
        Returns the highest-level valid decontractible graph in the hierarchy of the multilevel graph, combined
        with the level of the scheme that produced it.
        :return: the highest-level valid decontractible graph and the level of the scheme that produced it
        """
        for scheme in reversed(self._contraction_schemes):
            if scheme.is_valid():
                return scheme.dec_graph, scheme.level
        return self._dec_graph_0, 0

    def get_graph(self, level: int) -> Optional[DecGraph]:
        """
        Returns the reference of the decontractible graph at the given level in this multilevel graph.
        If the given level is 0, the base decontractible graph is returned, while if the given level is 1
        or higher, the decontractible graph resulting from the contraction scheme at the given level is returned,
        possibly after constructing it lazily.
        If the given level is not in the range of the contraction schemes in this multilevel graph, None is
        returned.

        The structure of the given decontractible graph should not be modified, as it may affect the integrity of
        the multilevel graph.

        :param level: the level of the decontractible graph to be returned
        :return: the decontractible graph at the given level
        """
        if level == 0:
            return self._dec_graph_0
        elif 1 <= level <= self.height():
            self.build_contraction_schemes(level)
            return self._contraction_schemes[level - 1].dec_graph
        else:
            return None

    def append_contraction_scheme(self, contraction_scheme):
        """
        Appends a new contraction scheme to the multilevel graph on top of the existing ones.

        The new contraction scheme is not immediately applied to the decontractible graph at the previous level,
        rather, the decontractible graph at the new level is constructed lazily only when the graph at the new level
        is requested.

        :param contraction_scheme: the contraction scheme to be appended
        """
        contraction_scheme.level = self.height() + 1
        self._contraction_schemes.append(contraction_scheme)

    def height(self) -> int:
        """
        Returns the height of the multilevel graph.
        The height of a multilevel graph is defined as the number of contraction schemes it has.
        """
        return len(self._contraction_schemes)

    def add_node(self, key: Any, **attr):
        """
        Adds a node to the base graph of the multilevel graph.
        If the node has a key that already exists in the base graph, it will not be added again.

        Changes to upper levels are not immediately reflected in the decontractible graphs, but rather lazily
        constructed when the decontractible graph at a certain level is requested.

        :param key: the key of the node to be added
        :param attr: the attributes to assign to the node
        """
        if key not in self._dec_graph_0.V:
            new_node = Supernode(key, level=0, **attr)
            self._dec_graph_0.add_node(new_node)
            self._base_update_quadruple.add_v_plus(new_node)
            self._invalidate_all_schemes()

    def remove_node(self, key: Any):
        """
        Removes a node from the base graph of the multilevel graph.
        If the node with the given key does not exist in the base graph, nothing happens.

        Changes to upper levels are not immediately reflected in the decontractible graphs, but rather lazily
        constructed when the decontractible graph at a certain level is requested.

        :param key: the key of the node to be removed
        """
        if key in self._dec_graph_0.V:
            old_node = self._dec_graph_0.V[key]
            self._dec_graph_0.remove_node(old_node)
            self._base_update_quadruple.add_v_minus(old_node)
            self._invalidate_all_schemes()

    def add_edge(self, tail_key: Any, head_key: Any, **attr):
        """
        Adds a directed edge between nodes having the given keys to the base graph of the multilevel graph.
        If the edge between the nodes with the given keys already exists in the base graph, it will not be added again.
        If one or both of the nodes with the given keys do not exist in the base graph, they are added as new nodes.

        Changes to upper levels are not immediately reflected in the decontractible graphs, but rather lazily
        constructed when the decontractible graph at a certain level is requested.

        :param tail_key: the key of the tail node of the edge to be added
        :param head_key: the key of the head node of the edge to be added
        :param attr: the attributes to assign to the edge
        """
        self.add_node(tail_key)
        self.add_node(head_key)
        if (tail_key, head_key) not in self._dec_graph_0.E:
            new_edge = Superedge(self._dec_graph_0.V[tail_key], self._dec_graph_0.V[head_key], level=0, **attr)
            self._dec_graph_0.add_edge(new_edge)
            self._base_update_quadruple.add_e_plus(new_edge)
            self._invalidate_all_schemes()

    def remove_edge(self, tail_key: Any, head_key: Any):
        """
        Removes the directed edge between nodes having the given keys from the base graph of the multilevel graph.
        If one of the given keys does not exist as a node, or the edge between the nodes with the given
        keys does not exist in the base graph, nothing happens.

        Changes to upper levels are not immediately reflected in the decontractible graphs, but rather lazily
        constructed when the decontractible graph at a certain level is requested.

        :param tail_key: the key of the tail node of the edge to be removed
        :param head_key: the key of the head node of the edge to be removed
        """
        if (tail_key, head_key) in self._dec_graph_0.E:
            old_edge = self._dec_graph_0.E[(tail_key, head_key)]
            self._dec_graph_0.remove_edge(old_edge)
            self._base_update_quadruple.add_e_minus(old_edge)
            self._invalidate_all_schemes()

    def merge_graph(self, graph: nx.DiGraph):
        """
        Merges the given NetworkX directed graph into the base graph of the multilevel graph.
        If the given graph has nodes or edges that already exist in the base graph, they will not be added again.

        Changes to upper levels are not immediately reflected in the decontractible graphs, but rather lazily
        constructed when the decontractible graph at a certain level is requested.

        :param graph: the NetworkX graph to be merged into the base graph
        """
        for node in graph.nodes(data=True):
            self.add_node(node[0], **node[1])
        for edge in graph.edges(data=True):
            self.add_edge(edge[0], edge[1], **edge[2])

    def _invalidate_all_schemes(self):
        for scheme in self._contraction_schemes:
            scheme.invalidate()

    def __getitem__(self, level: int) -> Optional[DecGraph]:
        """
        Returns the reference of the decontractible graph at the given level in this multilevel graph.
        If the given level is 0, the base decontractible graph is returned, while if the given level is 1
        or higher, the decontractible graph resulting from the contraction scheme at the given level is returned.
        If the given level is not in the range of the contraction schemes in this multilevel graph, None is returned.

        The structure of the given decontractible graph should not be modified, as it may affect the integrity of
        the multilevel graph.

        :param level: the level of the decontractible graph to be returned
        :return: the decontractible graph at the given level
        """
        return self.get_graph(level)

    def __len__(self) -> int:
        """
            Returns the height of the multilevel graph.
            The height of a multilevel graph is defined as the number of contraction schemes it has.
        """
        return self.height()
