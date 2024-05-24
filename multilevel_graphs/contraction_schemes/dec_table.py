from typing import Iterable, Set
from multilevel_graphs.dec_graphs import Supernode


class DecTable:
    """
    A decontractible table is a data structure that represents a covering of nodes and stores
    the information of which nodes are in which set of nodes.
    This data structure can be used as a dictionary where the keys are the nodes and the values are the sets of nodes
    to which they belong.
    """
    def __init__(self, sets: Iterable[Iterable[Supernode]]):
        """
        Initializes a decontractible table with the given sets of nodes.
        The given set of nodes should be a covering of the nodes of a decontractible graph.

        :param sets: the covering of nodes
        """
        self._table = dict()
        for nodes_set in sets:
            for node in nodes_set:
                self._table.setdefault(node, set()).add(nodes_set)

        self.modified = set()

    def __getitem__(self, key: Supernode) -> Set[Set[Supernode]]:
        return self._table[key]

    def __setitem__(self, key: Supernode, value: Set[Set[Supernode]]):
        self._table[key] = value

    def __delitem__(self, key: Supernode):
        del self._table[key]

    def __iter__(self):
        return iter(self._table)

    def __len__(self):
        return len(self._table)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._table})"

    def items(self):
        return self._table.items()

    def keys(self):
        return self._table.keys()

    def values(self):
        return self._table.values()
