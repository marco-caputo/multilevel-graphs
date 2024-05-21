import networkx as nx
from multilevel_graphs import Supernode, Superedge
from multiprocessing import Pool

class DecGraph:
    
    def __init__(self):
        self._digraph = nx.DiGraph()
        self.V = set()
        self.E = set()

    def add_node(self, supernode: Supernode):
        """
        Adds a supernode to the decontractible graph.
            If the supernode has a key that is already in the graph, it will not be added again.

        :param supernode: the supernode to be added
        """
        self._digraph.add_node(supernode.key)
        self.V.add(supernode)

    def add_edge(self, superedge: Superedge):
        """
        Adds a superedge to the decontractible graph.
            If the superedge has a tail and head the key of which are already in the graph as an edge,
            it will not be added again.

        :param superedge: the superedge to be added
        """
        self._digraph.add_edge(superedge.tail.key, superedge.head.key)
        self.E.add(superedge)
    
    def height(self) -> int:
        """
        Returns the height of the decontractible graph.

        :return: the height of the decontractible graph
        """
        if not self.V:
            return 0
        else:
            with Pool() as p:
                return max(p.map(Supernode.height, self.V))