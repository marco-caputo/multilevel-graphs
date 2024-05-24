from typing import Iterable, Set

import setuptools.package_index

from multilevel_graphs.contraction_schemes import ComponentSet
from multilevel_graphs.dec_graphs import Supernode


class DecTable:
    """
    A decontractible table is a data structure that represents a covering of nodes and stores
    the information of which nodes are in which set of nodes.
    This data structure can be used as a dictionary where the keys are the nodes and the values are the sets of nodes
    to which they belong.
    """
    def __init__(self, sets: Iterable[ComponentSet], maximal: bool = False):
        """
        Initializes a decontractible table with the given set of component sets of nodes.
        The given set should be a covering of the nodes of a decontractible graph, and all the component sets
        should be distinct in terms of their contained supernodes.
        In case the maximal parameter is set to True, the table will only store the maximal sets of nodes
        among the given component sets.

        :param sets: the covering of nodes
        :param maximal: if True, only maximal sets of nodes are stored
        """
        self._table = dict()
        self.modified = set()
        if maximal:
            for c_sets in sets:
                self.add_maximal_set(c_sets)
        else:
            for c_set in sets:
                for node in c_set:
                    self._table.setdefault(node, set()).add(c_set)


    def add_maximal_set(self, c_set: ComponentSet):
        """
        Adds the given component set to the table only if it is maximal among the sets already in the table.
        If the given component is added to the table, sets already in the table that are subsets of the given component
        set are removed.
        A component set is maximal if it is not a subset of any other component set in the table.

        :param c_set: the component set to add
        """
        if len(set.intersection(*[self._table.get(node, set()) for node in c_set])) == 0:
            pass # TODO: finish this method

    def __getitem__(self, key: Supernode) -> Set[ComponentSet]:
        return self._table[key]

    def __setitem__(self, key: Supernode, value: Set[ComponentSet]):
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
