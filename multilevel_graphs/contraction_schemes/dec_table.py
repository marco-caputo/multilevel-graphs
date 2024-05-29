from typing import Iterable, Set, Dict

from multilevel_graphs.contraction_schemes import ComponentSet
from multilevel_graphs.dec_graphs import Supernode


class DecTable:
    """
    A decontractible table is a data structure that represents a covering of nodes and stores
    the information of which nodes are in which set of nodes.
    This data structure can be used as a dictionary where the keys are the nodes and the values are the sets of nodes
    to which they belong.
    """
    _table: Dict[Supernode, Set[ComponentSet]]
    modified: Set[Supernode]

    def __init__(self, sets: Iterable[ComponentSet], maximal: bool = False):
        """
        Initializes a decontractible table with the given set of component sets of nodes.
        The given set should be a covering of the nodes of a decontractible graph, and all the component sets
        should be distinct in terms of their contained supernodes.
        In case the maximal parameter is set to True, the table will only track the maximal sets of nodes
        among the given component sets.

        :param sets: the covering of nodes
        :param maximal: if True, only maximal sets of nodes are stored
        """
        self._table = dict()
        self.modified = set()

        if maximal:
            for c_set in sets:
                self.add_maximal_set(c_set)
        else:
            for c_set in sets:
                self.add_set(c_set)

        self.modified.clear()

    def add_set(self, c_set: ComponentSet, maximal: bool = False):
        """
        Adds the given component set to the table tracked sets.
        The method behaves differently depending on the maximal parameter:

        - When maximal is set to False: if the given component set is already in the table, nothing happens.
        Rows of the table that are modified due to the addition of the given component set are tracked in the
        modified set.

        - When maximal is set to True: adds the given component set to the table only if it is maximal among the sets
        already tracked in the table.
        If the given component is added to the table, sets already tracked in the table that are subsets of the given
        component set are removed.
        A component set is maximal if it is not a subset of any other component set in the table.
        Rows of the table that are modified due to the possible addition and removals are tracked in the modified set.

        :param c_set: the component set to add
        :param maximal: if True, only maximal sets of nodes are stored and maintained
        """
        if maximal:
            self.add_maximal_set(c_set)
        else:
            self.add_non_maximal_set(c_set)

    def add_non_maximal_set(self, c_set: ComponentSet):
        """
        Adds the given component set to the table tracked sets.
        If the given component set is already in the table, nothing happens.
        Rows of the table that are modified due to the addition of the given component set are tracked in the
        modified set.

        :param c_set: the component set to add
        """
        for node in c_set:
            self._table.setdefault(node, set()).add(c_set)
            self.modified.add(node)

    def add_maximal_set(self, c_set: ComponentSet):
        """
        Adds the given component set to the table only if it is maximal among the sets already tracked in the table.
        If the given component is added to the table, sets already tracked in the table that are subsets of the given
        component set are removed.
        A component set is maximal if it is not a subset of any other component set in the table.
        Rows of the table that are modified due to the possible addition and removals are tracked in the
        modified set.

        :param c_set: the component set to add
        """
        if len(set.intersection(*[self._table.get(node, set()) for node in c_set])) == 0:
            subsets = self._find_subsets(c_set)
            for subset in subsets:
                self.remove_set(subset)
            self.add_set(c_set)

    def remove_set(self, c_set: ComponentSet):
        """
        Removes the given component set from the table tracked sets.
        If the given component set is not in the table, nothing happens.
        Rows of the table that are modified due to the removal of the given component set are tracked in the
        modified set.

        :param c_set: the component set to remove
        """
        for node in c_set:
            self._table.get(node, set()).discard(c_set)
            self.modified.add(node)

    def _find_subsets(self, c_set: ComponentSet) -> Set[ComponentSet]:
        """
        Returns the subsets of the given component set that are already tracked in the table.

        :param c_set: the component set
        :return: the subsets of the given component set
        """
        t_count = dict()
        for node in c_set:
            for c_set in self._table.get(node, set()):
                t_count[c_set] = t_count.get(c_set, 0) + 1

        subsets = set()
        for c_set, count in t_count.items():
            if count == len(c_set):
                subsets.add(c_set)

        return subsets

    def get_all_c_sets(self) -> Set[ComponentSet]:
        """
        Returns all the unique component sets tracked in this table.

        :return: all the unique component sets tracked in this table
        """
        return set.union(*self._table.values())

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

    def keys(self) -> Iterable[Supernode]:
        return self._table.keys()

    def values(self) -> Iterable[Set[ComponentSet]]:
        return self._table.values()
