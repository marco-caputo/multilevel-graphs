import networkx as nx
from typing import List, Optional, Any, Tuple, Set
from multilevel_graphs import DecGraph, Supernode, Superedge, ContractionScheme
from multilevel_graphs.contraction_schemes import UpdateQuadruple, ComponentSet


class MultilevelGraph:
    """
    A multilevel graph is a hierarchical data structure that represents a sequence of decontractible graphs
    produced by a series of contraction schemes (or contraction functions) applied to a base graph.

    More formally, a multi-level graph M is a couple (G, Γ) where

    - G is a directed graph
    - Γ = < fc_1, fc_2, ..., fc_k > is a sequence of contraction functions

    A multi-level graph M has an height h(M) = k, where k is the number of contraction functions in the sequence Γ.
    If we refer as G_i the decontractible graph of the multi-level graph M at level i, where 0 <= i <= k, then
    G_0 = G and G_i, with 0 < i <= k, is the decontractible graph produced by the i-th contraction function in the sequence Γ
    (1-indexed).

    The main operations that can be performed by a multi-level graph are:

     - The retrival of information at a certain level, such as the decontractible graph or the component sets of the
       contraction scheme at that level.
     - The modification of the base graph, such as the addition or removal of nodes and edges, and the consequent
       update of the decontractible graphs at the upper levels.

    In this implementation, once the graph at the base level is defined along with the sequence of contraction
    functions, the decontractible graphs at each level are lazily constructed when requested, as well as the component
    sets of the contraction schemes. Updates are also lazily propagated to the upper levels.
    To gain control of when the computation of the decontractible graphs is performed, the method
    ``build_contraction_schemes`` can be used to build the decontractible graphs from the base level up to a certain
    level.

    Examples
    --------
    A multilevel graph can be created from a NetworkX graph and a sequence of contraction schemes. For instance
    a multi-level graph of height 2 can be instantiated as follows::

        import networkx as nx
        from multilevel_graphs import MultilevelGraph, CliquesContractionScheme, SCCsContractionScheme

        nx_graph = nx.DiGraph()
        nx_graph.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)])
        ml_graph = MultilevelGraph(nx_graph, [CliquesContractionScheme(), SCCsContractionScheme()])

    Alternatively, a multilevel graph can be created from a NetworkX graph and the contraction schemes can be appended
    subsequently. In the following example, the resulting multilevel graph is equivalent to the one created in the
    previous example::

        import networkx as nx
        from multilevel_graphs import MultilevelGraph, CliquesContractionScheme, SCCsContractionScheme

        nx_graph = nx.DiGraph()
        nx_graph.add_edges_from([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5)])
        ml_graph = MultilevelGraph(nx_graph)
        ml_graph.append_contraction_scheme(CliquesContractionScheme())
        ml_graph.append_contraction_scheme(SCCsContractionScheme())

    The decontractible graph at a certain level can be retrieved using the ``get_graph`` method or the [] notation::

        dec_graph_1 = ml_graph.get_graph(1)
        dec_graph_2 = ml_graph[2]

    Note that the [] notation will return a reference to the decontractible graph, resulting in a performance gain,
    while the ``get_graph`` method will return a deep copy of the decontractible graph. For this reason, is
    recommended to use the [] notation when the returned decontractible graph is not going to be modified.

    Once the multilevel graph is created, nodes and edges can be added or removed from the base graph indicating
    the key of the nodes and the attributes of the nodes and edges.
    For instance, a new node can be added to the base graph as follows::

        ml_graph.add_node(6, color='red')

    Updates to the base graph will be lazily propagated to the upper levels, and further requests for the
    decontractible graph at a certain level will trigger the computation of the decontractible graph at that level.
    """
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
            self._contraction_schemes[i].level = i + 1

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
        vs = dict(map(lambda c: (c[0], Supernode(key=c[0], level=0, **c[1])), graph.nodes(data=True)))
        es = dict(map(lambda t: ((t[0], t[1]), Superedge(tail=vs[t[0]], head=vs[t[1]], level=0, **t[2])),
                      graph.edges(data=True)))
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
            update_q = self._contraction_schemes[i-1].update_quadruple if i > 0 else self._base_update_quadruple

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

    def get_graph(self, level: int, deepcopy: bool = True) -> Optional[DecGraph]:
        """
        Returns the decontractible graph at the given level in this multilevel graph.
        If the given level is 0, the base decontractible graph is returned, while if the given level is 1
        or higher, the decontractible graph resulting from the contraction scheme at the given level is returned,
        possibly after constructing it lazily.
        If the given level is not in the range of the contraction schemes in this multilevel graph, None is
        returned.

        If the ``deepcopy`` parameter is set to True, a deep copy of the decontractible graph is returned, otherwise,
        the returned decontractible graph will be a reference to the original one in this multi-level graph,
        and hence the structure of the returned decntractible graph should not be modified, as it may affect the
        integrity of the multilevel graph.
        In both cases, the returned decontractible graph will be navigable towards upper levels up to the highest
        valid level through the ``supernode`` attribute of supernodes.
        For levels that are not up-to-date, the supernode references may be out-to-date as well.

        Note that setting the ``deepcopy`` parameter to True may have a performance impact, as the decontractible graph
        is recursively copied, including its supernodes, superedges and the component sets of the supernodes.

        :param deepcopy: if True, a deep copy of the decontractible graph is returned
        :param level: the level of the decontractible graph to be returned
        :return: the decontractible graph at the given level
        """
        if level < 0 or level > self.height():
            return None

        if level == 0 and not deepcopy:
            return self._dec_graph_0
        else:
            self.build_contraction_schemes(level)
            if deepcopy:
                current_level = self._highest_valid_graph()[1]
                deepcopy_graph = self._contraction_schemes[current_level - 1].dec_graph.deepcopy() if current_level > 0 \
                    else self._dec_graph_0.deepcopy()
                while current_level != level:
                    current_level -= 1
                    deepcopy_graph = deepcopy_graph.complete_decontraction()
                return deepcopy_graph
            else:
                return self._contraction_schemes[level - 1].dec_graph

    def get_component_sets(self, level: int) -> Optional[Set[ComponentSet]]:
        """
        Returns the set of component sets of the decontractible graph recognized by the contraction scheme at the
        given level in this multilevel graph.
        If the given level is 0, None is returned, as the base decontractible graph does not have component sets.
        If the given level is 1 or higher, the component sets of the contraction scheme at the given level,
        composed of nodes at the immediate lower level, are returned.
        If the given level is not in the range of the contraction schemes in this multilevel graph, None is returned.

        The ComponentSet objects in the returned set are shallow copies of the original sets, and changes to the nodes
        in the set may affect the integrity of the multilevel graph.

        Note that this operation causes the decontractible graph at the given level to be constructed, if it has not.

        :param level: the level of the decontractible graph to be returned
        :return: the list of component sets of the decontractible graph at the given level
        """
        if 1 <= level <= self.height():
            self.build_contraction_schemes(level)
            return set([c_set.copy() for c_set in
                        self._contraction_schemes[level-1].component_sets_table.get_all_c_sets()])
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
        self._contraction_schemes.append(contraction_scheme.clone())
        self._contraction_schemes[-1].level = self.height()

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
        All edges that have the node as tail or head at the base graph will be removed as well.
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

        Note that this operation is equivalent to the ``get_graph`` method with the ``deepcopy`` parameter set to False.

        :param level: the level of the decontractible graph to be returned
        :return: the decontractible graph at the given level
        """
        return self.get_graph(level, deepcopy=False)

    def __len__(self) -> int:
        """
            Returns the height of the multilevel graph.
            The height of a multilevel graph is defined as the number of contraction schemes it has.
        """
        return self.height()
