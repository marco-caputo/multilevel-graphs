from typing import Optional

from multilevel_graphs.DecGraph import DecGraph


class Supernode:
    def __init__(self, key, dec_graph: DecGraph = DecGraph(), supernode: Optional['Supernode'] = None, **attr):
        self.key = key
        self.dec_graph = dec_graph
        self.supernode = supernode
        for k, v in attr.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return str(self.key)
