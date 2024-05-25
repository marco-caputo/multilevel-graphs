from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, Set

from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from multilevel_graphs.contraction_schemes import DecTable


class ContractionScheme(ABC):
    def __init__(self,
                 supernode_attr_function: Callable[[Supernode], Dict[str, Any]] = None,
                 superedge_attr_function: Callable[[Superedge], Dict[str, Any]] = None,
                 c_set_attr_function: Callable[[Set[Supernode]], Dict[str, Any]] = None):
        """
        Initializes a contraction scheme based on the contraction function
        defined for this scheme.

        :param supernode_attr_function: a function that returns the attributes to assign to each supernode of this scheme
        :param superedge_attr_function: a function that returns the attributes to assign to each superedge of this scheme
        :param c_set_attr_function: a function that returns the attributes to assign to each component set of this scheme
        """
        self._supernode_id_counter = 0
        self._component_set_id_counter = 0
        self._supernode_attr_function = supernode_attr_function if supernode_attr_function else lambda x: {}
        self._superedge_attr_function = superedge_attr_function if superedge_attr_function else lambda x: {}
        self._c_sets_attr_function = c_set_attr_function if c_set_attr_function else lambda x: {}
        self.level = 0
        self.dec_graph = DecGraph()
        self.contraction_sets_table = DecTable()
        self.supernode_table = dict()
        self.valid = False

    @property
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
    def contraction_function(self, dec_graph: DecGraph) -> DecTable:
        """
        Returns a dictionary of contraction sets for the given decontractible graph
        according to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        """
        pass

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

    def contract(self, dec_graph: DecGraph) -> DecGraph:
        """
        Modifies the state of this contraction scheme constructing a decontractible from the given decontractible
        graph according to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        :return: the contracted decontractible graph
        """
        self.contraction_sets_table = self.contraction_function(dec_graph)
        self.dec_graph = self._make_dec_graph(self.contraction_sets_table, dec_graph)
        self.update_attr()
        self.valid = True
        return self.dec_graph

    def is_valid(self):
        return self.valid

    def invalidate(self):
        self.valid = False

    def _make_dec_graph(self, dec_table: DecTable, dec_graph: DecGraph) -> DecGraph:
        """
        Constructs a decontractible graph from the given decontractible graph
        and the table containing the mapping between nodes and their set of contraction sets.

        :param dec_table: a table of contraction sets
        :param dec_graph: the decontractible graph to be contracted
        """
        self.supernode_table = dict()
        contracted_graph = DecGraph()

        # For each node, we assign it to a supernode corresponding to the set of component sets
        for node, set_of_sets in dec_table:
            f_set_of_sets = frozenset(set_of_sets)
            if f_set_of_sets not in self.supernode_table:
                supernode = \
                    Supernode(key=str(self.level) + "_" + self.contraction_name + "_" + str(self._get_supernode_id()),
                              level=self.level,
                              set_of_sets=f_set_of_sets)

                self.supernode_table[f_set_of_sets] = supernode
                contracted_graph.add_node(supernode)
            else:
                supernode = self.supernode_table[f_set_of_sets]

            supernode.add_node(node)
            node.supernode = supernode

        # For each edge, we assign it to a superedge if the tail and head are in different supernodes,
        # otherwise we assign it to the supernode containing both tail and head.
        for edge in dec_graph.edges():
            tail = edge.tail
            head = edge.head
            if tail.supernode != head.supernode:
                contracted_graph.E.setdefault((tail.supernode.key, head.supernode.key),
                                              Superedge(tail.supernode,
                                                        head.supernode,
                                                        level=self.level)) \
                    .add_edge(edge)
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
        for c_set in self.contraction_sets_table:
            c_set.update(**self._c_sets_attr_function(c_set))
