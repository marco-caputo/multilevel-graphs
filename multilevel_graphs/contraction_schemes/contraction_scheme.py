from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Set, Optional, FrozenSet

from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import CompTable, UpdateQuadruple, ComponentSet


class ContractionScheme(ABC):
    """
    An abstract class for contraction schemes.
    A contraction scheme is a layer of a multilevel graph that defines how the nodes and edges of the graph are
    contracted into supernodes and superedges, respectively.
    More formally, a contraction scheme is a contraction function fc defined on the domain of decontractible graphs
    and codomain of contracted decontractible graphs, which, given a decontractible graph G, returns a new
    decontractible graph G' that is a contraction of G.

    Along with the definition of the contraction function, provided by the method contraction_function, a contraction
    scheme should define methods to update the contracted decontractible graph according to the changes in the lower
    level decontractible graph. Those methods are ``_update_added_node``, ``_update_removed_node``,
    ``_update_added_edge`` and ``_update_removed_edge``.

    When a contraction scheme is constructed, it can be initialized with attribute functions for supernodes, superedges
    and component sets. These functions produce a dictionary of key-value pairs that are used to assign attributes to
    the supernodes and superedges of the produced contracted decontractible graph, as well as to the component sets
    tracked by the component set table of the contraction scheme.

    Attributes
    ----------
    level : Optional[int]
        the level of the contraction scheme in the multilevel graph. Automatically set by the multilevel graph when
        the contraction scheme is added to it.
    dec_graph : Optional[DecGraph]
        the contracted decontractible graph produced by this contraction scheme.
    component_sets_table : Optional[CompTable]
        the component set table of this contraction scheme, that tracks the current state of the component sets
        recognized by the contraction scheme.
    supernode_table : Dict[FrozenSet[ComponentSet], Supernode]
        a dictionary that maps the bijection between sets of component sets and the supernodes of the contracted
        decontractible graph produced by this contraction scheme.
    update_quadruple : UpdateQuadruple
        a quadruple of four sets that tracks the changes in the supernodes and superedges of the contracted
        decontractible graph. Used as a buffer to store the changes to send to the immediate upper level of the
        multilevel graph the contraction scheme is part of.

    Examples
    --------
    Let CliquesContractionScheme and SCCsContractionScheme be sample contraction scheme implementations, they can be
    used to define a multilevel graph as follows::

        from multilevel_graphs import MultilevelGraph, SCCsContractionScheme, CliquesContractionScheme
        import networkx as nx

        nx_graph = nx.DiGraph()
        nx_graph.add_edges_from([(1, 2), (2, 3), (3, 1)])

        scheme_1 = CliquesContractionScheme()
        scheme_2 = SCCsContractionScheme()
        ml_graph = MultilevelGraph(nx_graph, [scheme_1, scheme_2])

    The definition of the contraction scheme could also include attribute functions for supernodes, superedges and
    component sets::

        scheme = SCCsContractionScheme(
            supernode_attr_function= lambda n: {'size': len(n)},
            superedge_attr_function= lambda e: {'weight': sum([edge['weight'] for edge in e.edges()])},
            c_set_attr_function= lambda c_set: {'size': len(c_set)}
        )
    """
    level: Optional[int]
    dec_graph: Optional[DecGraph]
    component_sets_table: Optional[CompTable]
    supernode_table: Dict[FrozenSet[ComponentSet], Supernode]
    update_quadruple: UpdateQuadruple

    _supernode_id_counter: int
    _component_set_id_counter: int
    _supernode_attr_function: Callable[[Supernode], Dict[str, Any]]
    _superedge_attr_function: Callable[[Superedge], Dict[str, Any]]
    _c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]]
    _deleted_subnodes: Dict[Supernode, Set[Supernode]]

    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None):
        """
        Initializes a contraction scheme based on the contraction function defined for this scheme.

        :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
        :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
        :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
        """
        self._supernode_id_counter = 0
        self._component_set_id_counter = 0
        self._supernode_attr_function = supernode_attr_function if supernode_attr_function else lambda x: {}
        self._superedge_attr_function = superedge_attr_function if superedge_attr_function else lambda x: {}
        self._c_set_attr_function = c_set_attr_function if c_set_attr_function else lambda x: {}
        self._deleted_subnodes = dict()
        self._valid = False
        self.level = None
        self.dec_graph = None
        self.component_sets_table = None
        self.supernode_table = dict()
        self.update_quadruple = UpdateQuadruple()

    @abstractmethod
    def contraction_name(self) -> str:
        """
        Returns the name of the contraction scheme.
        The name should be unique among all the implementations of the ContractionScheme class.
        The name of the contraction scheme is used as part of the key for each supernode in the
        decontractible graph of this contraction scheme.

        :return: the name of the contraction scheme
        """
        pass

    @abstractmethod
    def clone(self):
        """
        Instantiates and returns a new contraction scheme with the same starting attributes as this one,
        such as attribute functions and others based on the implementation.
        The new contraction scheme does not preserve any information about the contraction sets or the
        decontractible graph of the clones one.

        This method is used internally by the multilevel graph to create new contraction schemes based on their
        construction parameters and preserve their encapsulation.

        :return: a new contraction scheme with the same starting attributes as this one
        """
        pass

    @abstractmethod
    def contraction_function(self, dec_graph: DecGraph) -> CompTable:
        """
        Returns component set table for the given decontractible graph according to this contraction scheme.
        The component set table is a mapping between nodes and their corresponding collection of component sets
        the node is part of, according to the contraction scheme.

        The returned component set table should provide a covering of the nodes of the decontractible graph, where
        each node appears as the key of a row of the table, and all the sets of component sets provided as values
        should be non-empty.

        All the component sets tracked by the table should also be distinct in terms of their contained supernodes.

        :param dec_graph: the decontractible graph to be contracted
        """
        pass

    @abstractmethod
    def _update_added_node(self, node: Supernode):
        """
        Updates the structure of the decontractible graph of this contraction scheme according to the addition
        of the given supernode at the immediate lower level.

        The new added supernode should be immediately assigned to a new supernode in the decontractible graph of
        this contraction scheme.
        Temporary supernodes created in this method should not be tracked by the supernode table of this scheme.

        :param node: the supernode added to the lower level decontractible graph
        """
        pass

    @abstractmethod
    def _update_removed_node(self, node: Supernode):
        """
        Updates the structure of the decontractible graph of this contraction scheme according to the removal
        of the given supernode at the immediate lower level.

        :param node: the supernode removed from the lower level decontractible graph
        """
        pass

    @abstractmethod
    def _update_added_edge(self, edge: Superedge):
        """
        Updates the structure of the decontractible graph of this contraction scheme according to the addition
        of the given superedge at the immediate lower level.

        :param edge: the superedge added to the lower level decontractible graph
        """
        pass

    @abstractmethod
    def _update_removed_edge(self, edge: Superedge):
        """
        Updates the structure of the decontractible graph of this contraction scheme according to the removal
        of the given superedge at the immediate lower level.

        :param edge: the superedge removed from the lower level decontractible graph
        """
        pass

    def update(self, update_quadruple: UpdateQuadruple) -> DecGraph:
        """
        Updates the structure of the decontractible graph of this contraction scheme according to the given
        update quadruple, indicating the changes in the supernodes and superedges of the decontractible graph at
        the immediate lower level.

        :param update_quadruple: the update quadruple indicating the changes in the lower level decontractible graph
        :return: the updated decontractible graph of this contraction scheme
        """
        for edge in update_quadruple.e_minus:
            self._update_removed_edge(edge)
        for node in update_quadruple.v_minus:
            self._update_removed_node(node)
        for node in update_quadruple.v_plus:
            self._update_added_node(node)
        for edge in update_quadruple.e_plus:
            self._update_added_edge(edge)

        self._update_graph()
        self.update_attr()
        self._valid = True

        return self.dec_graph

    def _get_supernode_id(self) -> int:
        """
        Returns a unique identifier for the supernodes of this contraction scheme.
        Each new identifier is tracked by incrementing the identifier counter.

        :return: a new unique identifier
        """
        self._supernode_id_counter += 1
        return self._supernode_id_counter

    def _get_component_set_id(self) -> int:
        """
        Returns a unique identifier for the component sets of this contraction scheme.
        Each new identifier is tracked by incrementing the identifier counter.

        :return: a new unique identifier
        """
        self._component_set_id_counter += 1
        return self._component_set_id_counter

    def _get_supernode_key(self):
        return (str(self.level)+"_" if self.level else "") \
            + self.contraction_name() + "_" \
            + str(self._get_supernode_id())

    def contract(self, dec_graph: DecGraph) -> DecGraph:
        """
        Modifies the state of this contraction scheme constructing a decontractible from the given decontractible
        graph according to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        :return: the contracted decontractible graph
        """
        self.component_sets_table = self.contraction_function(dec_graph)
        self.dec_graph = self._make_dec_graph(self.component_sets_table, dec_graph)
        self.update_attr()
        self._valid = True
        return self.dec_graph

    def is_valid(self):
        """
        Returns whether the decontractible graph of this contraction scheme is valid, that is, it has been
        contracted and is up-to-date with the changes in the lower level decontractible graph.

        :return: True if the decontractible graph is valid, False otherwise
        """
        return self._valid

    def invalidate(self):
        """
        Marks the decontractible graph of this contraction scheme as invalid, that is, it has not been contracted
        or is not up-to-date with the changes in the lower level decontractible graph.
        """
        self._valid = False

    def _make_dec_graph(self, dec_table: CompTable, dec_graph: DecGraph) -> DecGraph:
        """
        Constructs a decontractible graph from the given decontractible graph
        and the table containing the mapping between nodes and their set of contraction sets.

        :param dec_table: a table of contraction sets
        :param dec_graph: the decontractible graph to be contracted
        """
        self.supernode_table = dict()
        contracted_graph = DecGraph()

        # For each node, we assign it to a supernode corresponding to the set of component sets
        for node, set_of_c_sets in dec_table.items():
            f_component_sets = frozenset(set_of_c_sets)
            if f_component_sets not in self.supernode_table:
                supernode = \
                    Supernode(key=self._get_supernode_key(),
                              level=self.level,
                              component_sets=f_component_sets)

                self.supernode_table[f_component_sets] = supernode
                contracted_graph.add_node(supernode)
            else:
                supernode = self.supernode_table[f_component_sets]

            supernode.add_node(node)
            node.supernode = supernode

        # For each edge, we assign it to a superedge if the tail and head are in different supernodes,
        # otherwise we assign it to the supernode containing both tail and head.
        for edge in dec_graph.edges():
            tail = edge.tail
            head = edge.head
            if tail.supernode != head.supernode:
                contracted_graph.add_edge(Superedge(tail.supernode, head.supernode, level=self.level))
                contracted_graph.E[(tail.supernode.key, head.supernode.key)].add_edge(edge)
            else:
                tail.supernode.add_edge(edge)

        return contracted_graph

    def update_attr(self):
        """
        Updates the attributes of the supernodes, superedges and component sets of this contraction scheme.
        """
        for supernode in self.dec_graph.nodes():
            supernode.update(**self._supernode_attr_function(supernode))
        for superedge in self.dec_graph.edges():
            superedge.update(**self._superedge_attr_function(superedge))
        for c_set in self.component_sets_table.get_all_c_sets():
            c_set.update(**self._c_set_attr_function(set(c_set)))

    def _add_edge_in_superedge(self, tail_key: Any, head_key: Any, edge: Superedge):
        """
        Adds the given edge to the superedge in the decontractible graph of this contraction scheme having the given
        tail and head keys.
        If no such superedge is in the graph, it is added, and the quadruple is updated accordingly.

        :param tail_key: the key of the tail supernode of the superedge
        :param head_key: the key of the head supernode of the superedge
        :param edge: the edge to add
        """
        if (tail_key, head_key) not in self.dec_graph.E:
            new_superedge = Superedge(self.dec_graph.V[tail_key], self.dec_graph.V[head_key], level=self.level)
            self.dec_graph.add_edge(new_superedge)
            self.update_quadruple.add_e_plus(new_superedge)

        self.dec_graph.E[(tail_key, head_key)].add_edge(edge)

    def _remove_edge_in_superedge(self, tail_key: Any, head_key: Any, edge: Superedge):
        """
        Removes the given edge from the superedge in the decontractible graph of this contraction scheme having the
        given tail and head keys.
        If the superedge decontraction set becomes empty, it is removed from the graph, and the quadruple is updated
        accordingly.

        :param tail_key: the key of the tail supernode of the superedge
        :param head_key: the key of the head supernode of the superedge
        :param edge: the edge to remove
        """
        superedge = self.dec_graph.E[(tail_key, head_key)]
        superedge.remove_edge(edge)

        if not superedge.dec:
            self.dec_graph.remove_edge(superedge)
            self.update_quadruple.add_e_minus(superedge)

    def _add_supernode(self, component_sets: FrozenSet[ComponentSet]) -> Supernode:
        """
        Adds a supernode to the decontractible graph of this contraction scheme corresponding to the given set of
        component sets.
        The supernode is added to the graph and the supernode table, and the quadruple is updated accordingly.

        :param component_sets: the frozen set of component sets corresponding to the supernode
        :return: the added supernode
        """
        supernode = Supernode(key=self._get_supernode_key(),
                              level=self.level,
                              component_sets=component_sets)
        self.dec_graph.add_node(supernode)
        self.update_quadruple.add_v_plus(supernode)
        self.supernode_table[component_sets] = supernode
        return supernode

    def _remove_supernode(self, supernode: Supernode):
        """
        Removes the given supernode from the decontractible graph of this contraction scheme.
        The supernode is removed from the graph and the supernode table, and the quadruple is updated accordingly.

        :param supernode: the supernode to remove
        """
        self.dec_graph.remove_node(supernode)
        self.update_quadruple.add_v_minus(supernode)
        if supernode.component_sets in self.supernode_table:
            del self.supernode_table[supernode.component_sets]

    def _update_graph(self):
        """
        Updates the structure of the decontractible graph of this contraction scheme according to the changes
        in the component sets tracked by the component sets table.
        """
        old_supernodes: Dict[Supernode, Supernode] = dict()
        decontraction = self.dec_graph.complete_decontraction()

        for node in self.component_sets_table.modified:
            c_sets_of_node = frozenset(self.component_sets_table[node])

            if c_sets_of_node not in self.supernode_table:
                self._add_supernode(c_sets_of_node)

            old_supernodes[node] = node.supernode
            self._deleted_subnodes.setdefault(node.supernode, set()).add(node)

            node.supernode = self.supernode_table[c_sets_of_node]
            node.supernode.dec.add_node(node)

        for b in self.component_sets_table.modified:
            for edge in decontraction.in_edges(b):
                if edge.tail not in old_supernodes:

                    if edge.tail.supernode == old_supernodes[b]:
                        edge.tail.supernode.remove_edge(edge)
                    else:
                        self._remove_edge_in_superedge(edge.tail.supernode.key, old_supernodes[b].key, edge)

                    if edge.tail.supernode == b.supernode:
                        edge.tail.supernode.add_edge(edge)
                    else:
                        self._add_edge_in_superedge(edge.tail.supernode.key, b.supernode.key, edge)

            for edge in decontraction.out_edges(b):
                if edge.head in old_supernodes:

                    if old_supernodes[b] == old_supernodes[edge.head]:
                        old_supernodes[b].remove_edge(edge)
                    else:
                        self._remove_edge_in_superedge(old_supernodes[b].key, old_supernodes[edge.head].key, edge)

                    if b.supernode == edge.head.supernode:
                        b.supernode.add_edge(edge)
                    else:
                        self._add_edge_in_superedge(b.supernode.key, edge.head.supernode.key, edge)

                else:
                    if old_supernodes[b] == edge.head.supernode:
                        edge.head.supernode.remove_edge(edge)
                    else:
                        self._remove_edge_in_superedge(old_supernodes[b].key, edge.head.supernode.key, edge)

                    if b.supernode == edge.head.supernode:
                        b.supernode.add_edge(edge)
                    else:
                        self._add_edge_in_superedge(b.supernode.key, edge.head.supernode.key, edge)

        for supernode, node_set in self._deleted_subnodes.items():
            for node in node_set:
                supernode.dec.remove_node(node)
            if not supernode.dec.nodes():
                self._remove_supernode(supernode)

        self._deleted_subnodes.clear()
        self.component_sets_table.modified.clear()
