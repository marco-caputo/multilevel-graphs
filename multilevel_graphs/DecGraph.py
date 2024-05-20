import networkx as nx
from multilevel_graphs import Supernode


class DecGraph:

    def __init__(self):
        self.digraph = nx.DiGraph()

    def add_node(self, supernode_for_adding: Supernode):
        attr = supernode_for_adding.attr
        attr['dec_graph'] = supernode_for_adding.dec_graph
        attr['supernode'] = supernode_for_adding.supernode
        self.digraph.add_node(supernode_for_adding.key, attr)
