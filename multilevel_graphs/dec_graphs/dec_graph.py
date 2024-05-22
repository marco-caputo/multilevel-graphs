from typing import Optional, Set

import networkx as nx


class DecGraph:

    def __init__(self, dict_V: dict = dict(), dict_E: dict = dict()):
        self._digraph = nx.DiGraph()
        self._digraph.add_nodes_from(dict_V.keys())
        self._digraph.add_edges_from(dict_E.keys())
        self.V = dict_V
        self.E = dict_E

    def nodes(self) -> Set['Supernode']:
        """
        Returns the set of supernodes in the decontractible graph.

        :return: the set of supernodes in the decontractible graph
        """
        return set(self.V.values())

    def edges(self) -> Set['Superedge']:
        """
        Returns the set of superedges in the decontractible graph.

        :return: the set of superedges in the decontractible graph
        """
        return set(self.E.values())

    def nodes_keys(self) -> Set:
        """
        Returns the set of keys of supernodes in the decontractible graph.

        :return: the set of keys of supernodes in the decontractible graph
        """
        return set(self.V.keys())

    def edges_keys(self) -> Set:
        """
        Returns the set of keys of superedges in the decontractible graph.

        :return: the set of keys of superedges in the decontractible graph
        """
        return set(self.E.keys())

    def add_node(self, supernode: 'Supernode'):
        """
        Adds a supernode to the decontractible graph.
            If the supernode has a key that is already in the graph, it will not be added again.

        :param supernode: the supernode to be added
        """
        self.V.add(supernode.key, supernode)
        self._digraph.add_node(supernode.key)

    def add_edge(self, superedge: 'Superedge'):
        """
        Adds a superedge to the decontractible graph.
            If the superedge has a tail and head the key of which are already in the graph as an edge,
            it will not be added again.

        :param superedge: the superedge to be added
        """
        self.E.add((superedge.tail.key, superedge.head.key), superedge)
        self._digraph.add_edge(superedge.tail.key, superedge.head.key)

    def height(self) -> int:
        """
        Returns the height of the decontractible graph.

        :return: the height of the decontractible graph
        """
        if not self.V:
            return 0
        else:
            return max(map(Supernode.height, self.V))

    def remove_node(self, supernode: 'Supernode'):
        """
        Removes a supernode from the decontractible graph.
            If the supernode has a key which is not in the graph, rise a KeyError.
        :param supernode: the supernode to be removed
        """
        self.V.remove(supernode)
        self._digraph.remove_node(supernode.key)

    def remove_edge(self, superedge: 'Superedge'):
        """
        Removes a superedge from the decontractible graph.
            If the superedge has a tail and head the key of which are not in the graph as an edge,
            rise a KeyError.
        :param superedge: the superedge to be removed
        """
        self.E.pop((superedge.tail.key, superedge.head.key))
        self._digraph.remove_edge(superedge.tail.key, superedge.head.key)

    def height(self):
        """
        Returns the height of the decontractible graph represented by this supernode.

        :return: the height of the decontractible graph
        """
        return self.dec.height()


class Supernode:
    __slots__ = ('key', 'dec', 'supernode', 'attr')

    def __init__(self, key, dec: DecGraph = DecGraph(), supernode: Optional['Supernode'] = None, attr: dict = dict()):
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

    def add_node(self, supernode: 'Supernode'):
        """
        Adds a supernode to the decontractible graph represented by this supernode.
            If the supernode has a key that is already in the graph, it will not be added again.

        :param supernode: the supernode to be added
        """
        self.dec.add_node(supernode)

    def add_edge(self, edge_for_adding: 'Superedge'):
        """
        Adds a superedge to the decontractible graph represented by this supernode.
            If the superedge has a tail and head the key of which are already in the graph as an edge,
            it will not be added again.

        :param edge_for_adding:
        :return:
        """
        self.dec.add_edge(edge_for_adding)

    def remove_node(self, supernode: 'Supernode'):
        """
        Removes a supernode from the decontractible graph represented by this supernode.
            If the supernode has a key which is not in the graph, rise a KeyError.

        :param supernode: the supernode to be removed
        """
        self.dec.remove_node(supernode)

    def remove_edge(self, edge_for_removal: 'Superedge'):
        """
        Removes a superedge from the decontractible graph represented by this supernode.
            If the superedge has a tail and head the key of which are not in the graph as an edge,
            rise a KeyError.

        :param edge_for_removal: the superedge to be removed
        """
        self.dec.remove_edge(edge_for_removal)

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


class Superedge:
    __slots__ = ('tail', 'head', 'dec', 'attr')

    def __init__(self, tail: 'Supernode', head: 'Supernode', dec: Set['Superedge'] = set(), attr: dict = dict()):
        self.tail = tail
        self.head = head
        for e in dec:
            print(e)
            if e.tail not in self.tail.dec.nodes() or e.head not in self.head.dec.nodes():
                raise ValueError('The supernodes of the superedge to be added must be included in tail and head'
                                 'decontractions respectively.')
        self.dec = dec
        self.attr = attr

    def add_edge(self, superedge: 'Superedge'):
        """
        Adds a superedge to the superedge set represented by this superedge.
        If the superedge has a tail and head the key of which are already in the set, it will not be added again.

        :param superedge: the superedge to be added
        """
        if superedge.tail not in self.tail.dec.nodes() or superedge.head not in self.head.dec.nodes():
            raise ValueError('The supernodes of the superedge to be added must be included in tail and head'
                             'decontractions respectively.')
        self.dec.add(superedge)

    def remove_edge(self, superedge: 'Superedge'):
        """
        Removes a superedge from the superedge set represented by this superedge.
        If the superedge is not in the set, rise a KeyError.

        :param superedge: the superedge to be removed
        """
        self.dec.remove(superedge)

    def __eq__(self, other):
        return self.tail == other.tail and self.head == other.head

    def __hash__(self):
        return hash((self.tail, self.head))

    def __str__(self):
        return str(self.tail) + ' -> ' + str(self.head)
