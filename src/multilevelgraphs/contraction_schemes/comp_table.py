from typing import Iterable, Set, Dict, Callable, Generator

from src.multilevelgraphs.contraction_schemes import ComponentSet
from src.multilevelgraphs.dec_graphs import Supernode


class CompTable:
    """
    A component set table is a data structure associated with a particular layer of a multilevel graph that represents
    a covering of nodes at the immediate lower level and stores the information regarding which nodes are currently in
    which set of nodes.

    This data structure can be used as a dictionary where the keys are the nodes and the values are the sets of
    component set of nodes to which they belong.

    Attributes
    ----------
    modified : Set[Supernode]
        the set of nodes whose component sets have been modified in the rows of this table since the last update
    """
    modified: Set[Supernode]
    _table: Dict[Supernode, Set[ComponentSet]]

    def __init__(self, sets: Iterable[ComponentSet] = None, maximal: bool = False):
        """
        Initializes a component set table with the given set of component sets of nodes.
        The given set should be a covering of the nodes of a decontractible graph, and all the component sets
        should be distinct in terms of their contained supernodes.
        In case the maximal parameter is set to True, the table will only track the maximal sets of nodes
        among the given component sets.

        :param sets: the covering of nodes
        :param maximal: if True, only maximal sets of nodes are stored
        """
        self._table = dict()
        self.modified = set()

        if sets is not None:
            for c_set in sets:
                self.add_set(c_set, maximal=maximal)

            self.modified.clear()

    def add_set(self, c_set: ComponentSet, maximal: bool = False):
        """
        Adds the given component set to the table tracked sets.
        The method behaves differently depending on the maximal parameter:

        - When maximal is set to **False**: if the given component set is already in the table according to its key,
          nothing happens. Note that component sets with the same set of nodes and different keys are considered distinct
          and no distinct component sets with different set of nodes should be added to the same table.
          Rows of the table that are modified due to the addition of the given component set are tracked in the
          modified set.

        - When maximal is set to **True**: adds the given component set to the table only if it is maximal among the sets
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
        If the given component set is already in the table according to its key, nothing happens.
        Note that component sets with the same set of nodes and different keys are considered distinct
        and no distinct component sets with different set of nodes should be added to the same table.
        Rows of the table that are modified due to the addition of the given component set are tracked in the
        modified set.

        :param c_set: the component set to add
        """
        for node in c_set:
            self._table.setdefault(node, set()).add(c_set)
            self.modified.add(node)

    def add_maximal_set(self, c_set: ComponentSet, check_subsets: bool = True):
        """
        Adds the given component set to the table only if it is maximal among the sets already tracked in the table.
        If the given component is added to the table, sets already tracked in the table that are subsets of the given
        component set are removed.

        When the check_subset flag is set to False, this method does not check for subsets of the given
        component set to remove in the table while adding it.
        For this reason this option should only be used for a performance gain purposes when it is guaranteed
        that the given component set is not a subset of any other component set in the table.

        A component set is maximal if it is not a subset of any other component set in the table.
        Rows of the table that are modified due to the possible addition and removals are tracked in the
        modified set.

        :param c_set: the component set to add
        :param check_subsets: if True, the method does not check for subsets of the given component set to remove
        """
        # Finds the smallest set of component sets to reduce the workload of the intersection operation
        c_sets_of_nodes = [self._table.get(node, set()) for node in c_set]
        smallest_set = min(c_sets_of_nodes, key=len)

        if len(set.intersection(smallest_set, *c_sets_of_nodes)) == 0:
            if check_subsets:
                for subset in self._find_subsets(c_set):
                    self.remove_set(subset)
            self.add_non_maximal_set(c_set)

    def _find_subsets(self, c_set: ComponentSet) -> Generator[ComponentSet, None, None]:
        """
        Returns the subsets of the given component set that are already tracked in the table.

        :param c_set: the component set
        :return: the subsets of the given component set
        """
        t_count = dict()
        for node in c_set:
            for c_set in self._table.get(node, set()):
                t_count[c_set] = t_count.get(c_set, 0) + 1

        for c_set, count in t_count.items():
            if count == len(c_set):
                yield c_set

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

    def add_singletons(self, id_function: Callable[[], int]):
        """
        Creates and adds to this table singleton component sets for all the nodes that are not in any component set
        among the tracked sets.
        Note that only the nodes that have been tracked as modified are considered for this operation, since
        having empty set of component sets for a node is not a valid state in this table outside the update
        procedure of a contraction scheme.

        :param id_function: the function to generate unique identifiers for the new component sets
        """
        for node in self.modified:
            if not self._table.get(node):
                self.add_set(ComponentSet(id_function(), {node}))

    def get_all_c_sets(self) -> Set[ComponentSet]:
        """
        Returns all the unique component sets tracked in this table.

        :return: all the unique component sets tracked in this table
        """
        return set.union(*self._table.values(), set())

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
