from abc import ABC, abstractmethod
from multilevel_graphs.dec_graphs import DecGraph, Supernode, Superedge
from dec_table import DecTable


class ContractionScheme(ABC):
    def __init__(self, level: int):
        """
        Initializes a contraction scheme based on the contraction function
        defined for this scheme.

        :param level: the level of the contraction scheme in the multilevel graph where this scheme resides
        """
        self._id_counter = 0
        self.level = level
        self._dec_graph = None
        self.contraction_sets_table = None
        self.supernode_table = None
        self.valid = False

    @property
    @abstractmethod
    def contraction_name(self) -> str:
        """
        Returns the name of the contraction scheme.
        The name should be unique among all the implementations of the ContractionScheme class.
        The name of the contraction scheme is used as part of the key for each supernode in the
        decontractible graph of this contraction scheme.
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

    def _get_id(self) -> int:
        """
        Returns a unique identifier for the supernodes of this contraction scheme.
        Each new identifier is tracked by incrementing the identifier counter.

        :return: a new unique identifier
        """
        self._id_counter += 1
        return self._id_counter

    def contract(self, dec_graph: DecGraph) -> DecGraph:
        """
        Constructs a decontractible from the given decontractible graph according
        to this contraction scheme.

        :param dec_graph: the decontractible graph to be contracted
        :return: the contracted decontractible graph
        """
        self.contraction_sets_table = self.contraction_function(dec_graph)
        self._dec_graph = self._make_dec_graph(self.contraction_sets_table, dec_graph)
        self.valid = True
        return self._dec_graph

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

        # For each node, we assign it to a supernode corresponding to the set of sets
        for node, set_of_sets in dec_table:
            if set_of_sets not in self.supernode_table:
                supernode = \
                    Supernode(key=str(self.level) + "_" + self.contraction_name + "_" + str(self._get_id()),
                              level=self.level,
                              set_of_sets=set_of_sets)

                self.supernode_table[set_of_sets] = supernode
                contracted_graph.add_node(supernode)
            else:
                supernode = self.supernode_table[set_of_sets]

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
