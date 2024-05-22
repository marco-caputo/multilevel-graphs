import networkx as nx
from multilevel_graphs.dec_graphs import Supernode, Superedge


class DecGraph:
    
    def __init__(self, dict_V: dict = dict(), dict_E: dict = dict()):
        self._digraph = nx.DiGraph()
        self._digraph.add_nodes_from(dict_V.keys())
        self._digraph.add_edges_from(dict_E.keys())
        self.V = dict_V
        self.E = dict_E

    def add_node(self, supernode: Supernode):
        """
        Adds a supernode to the decontractible graph.
            If the supernode has a key that is already in the graph, it will not be added again.

        :param supernode: the supernode to be added
        """
        self.V.add(supernode.key, supernode)
        self._digraph.add_node(supernode.key)

    def add_edge(self, superedge: Superedge):
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

    def remove_node(self, supernode: Supernode):
        """
        Removes a supernode from the decontractible graph.
            If the supernode has a key which is not in the graph, rise a KeyError.
        :param supernode: the supernode to be removed
        """
        self.V.remove(supernode)
        self._digraph.remove_node(supernode.key)

    def remove_edge(self, superedge: Superedge):
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
