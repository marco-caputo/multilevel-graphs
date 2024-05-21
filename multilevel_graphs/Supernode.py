from typing import Optional

from multilevel_graphs.DecGraph import DecGraph, Superedge, Supernode


class Supernode:
    __slots__ = ('key', 'dec_graph', 'supernode', 'attr')

    def __init__(self, key, dec: DecGraph = DecGraph(), supernode: Optional[Supernode] = None, **attr):
        """
        Initializes a supernode.

        :param key: an immutable value representing the key label of the supernode. It is used to identify the
        supernode in the decontractible graph and should be unique in the decontractible graph where the
        supernode resides.
        :param dec_graph: the decontractible graph represented by this supernode
        :param supernode: the supernode that this supernode into
        :param attr: a dictionary of attributes to be added to the supernode
        """
        self.key = key
        self.dec = dec
        self.supernode = supernode
        self.attr = attr

    def add_node(self, supernode: Supernode):
        """
        Adds a supernode to the decontractible graph represented by this supernode.
            If the supernode has a key that is already in the graph, it will not be added again.

        :param supernode: the supernode to be added
        """
        self.dec_graph.add_node(supernode)

    def add_edge(self, edge_for_adding: Superedge):
        """
        Adds a superedge to the decontractible graph represented by this supernode.
            If the superedge has a tail and head the key of which are already in the graph as an edge,
            it will not be added again.

        :param edge_for_adding:
        :return:
        """
        self.dec_graph.add_edge(edge_for_adding)

    def remove_node(self, supernode: Supernode):
        """
        Removes a supernode from the decontractible graph represented by this supernode.
            If the supernode has a key which is not in the graph, rise a KeyError.

        :param supernode: the supernode to be removed
        """
        self.dec_graph.remove_node(supernode)

    def remove_edge(self, edge_for_removal: Superedge):
        """
        Removes a superedge from the decontractible graph represented by this supernode.
            If the superedge has a tail and head the key of which are not in the graph as an edge,
            rise a KeyError.

        :param edge_for_removal: the superedge to be removed
        """
        self.dec_graph.remove_edge(edge_for_removal)

    def height(self):
        """
        Returns the height of the decontractible graph represented by this supernode.

        :return: the height of the decontractible graph
        """
        return self.dec.height()

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return str(self.key)
