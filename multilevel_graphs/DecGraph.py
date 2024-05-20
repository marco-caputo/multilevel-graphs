import networkx as nx
from multilevel_graphs import Supernode


class DecGraph:

    def __init__(self):
        self._digraph = nx.DiGraph()
        self.V = set()
        self.E = set()

    def add_node(self, node_for_adding: Supernode):
        self.digraph.add_node(node_for_adding.key)
        self.V.add(node_for_adding)

'''
    def add_edge(self, edge_for_adding: Superedge):
        self.digraph.add_edge(edge_for_adding.tail.key, edge_for_adding.head.key)
        self.E.add(edge_for_adding)
'''
