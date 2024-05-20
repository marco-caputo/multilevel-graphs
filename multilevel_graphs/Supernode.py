from typing import Optional

from multilevel_graphs.DecGraph import DecGraph


class Supernode:
    def __init__(self, key, dec_graph: DecGraph = DecGraph(), supernode: Optional['Supernode'] = None, **attr):
        self.key = key
        self.dec_graph = dec_graph
        self.supernode = supernode
        self.attr = attr

    def __eq__(self, other):
        return self.key == other.key
