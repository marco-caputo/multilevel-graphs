from typing import Iterable, Set

from src.multilevelgraphs.dec_graphs import Supernode, Superedge


class UpdateQuadruple:
    """
    A quadruple of sets of supernodes and superedges that represent an update in the decontractible graph of a
    contraction scheme and tracks the changes in the supernodes and superedges of the decontractible graph that
    are not yet considered by higher level contraction schemes.

    The sets are:

    - ``v_plus`` : the supernodes tha have been added to the decontractible graph
    - ``v_minus`` : the supernodes that have been removed from the decontractible graph
    - ``e_plus`` : the superedges that have been added to the decontractible graph
    - ``e_minus`` : the superedges that have been removed from the decontractible graph

    The update quadruple is managed in order to maintain itself minimal, that is, ``v_plus`` and ``v_minus``
    are disjoint and ``e_plus`` and ``e_minus`` are disjoint.
    """
    _v_plus: Set[Supernode]
    _v_minus: Set[Supernode]
    _e_plus: Set[Superedge]
    _e_minus: Set[Superedge]

    def __init__(self,
                 v_plus: Iterable[Supernode] = None,
                 v_minus: Iterable[Supernode] = None,
                 e_plus: Iterable[Superedge] = None,
                 e_minus: Iterable[Superedge] = None):
        self._v_plus = set(v_plus) if v_plus else set()
        self._v_minus = set(v_minus) if v_minus else set()
        self._e_plus = set(e_plus) if e_plus else set()
        self._e_minus = set(e_minus) if e_minus else set()

    @property
    def v_plus(self) -> Set[Supernode]:
        """
        Returns a copy of the set of supernodes that have been added.
        :return: a copy of the set of supernodes that have been added
        """
        return set(self._v_plus)

    @property
    def v_minus(self) -> Set[Supernode]:
        """
        Returns a copy of the set of supernodes that have been removed.
        :return: a copy of the set of supernodes that have been removed
        """
        return set(self._v_minus)

    @property
    def e_plus(self) -> Set[Superedge]:
        """
        Returns a copy of the set of superedges that have been added.
        :return: a copy of the set of superedges that have been added
        """
        return set(self._e_plus)

    @property
    def e_minus(self) -> Set[Superedge]:
        """
        Returns a copy of the set of superedges that have been removed.
        :return: a copy of the set of superedges that have been removed
        """
        return set(self._e_minus)

    def add_v_plus(self, supernode: Supernode):
        """
        Adds a supernode to the set of supernodes that have been added.
        If the supernode is in the set of supernodes that have been removed, it is removed from that set instead.

        :param supernode: the supernode to add
        """
        if supernode not in self._v_minus:
            self._v_plus.add(supernode)
        else:
            self._v_minus.remove(supernode)

    def add_v_minus(self, supernode: Supernode):
        """
        Adds a supernode to the set of supernodes that have been removed.
        If the supernode is in the set of supernodes that have been added, it is removed from that set instead.

        :param supernode: the supernode to add
        """
        if supernode not in self._v_plus:
            self._v_minus.add(supernode)
        else:
            self._v_plus.remove(supernode)

    def add_e_plus(self, superedge: Superedge):
        """
        Adds a superedge to the set of superedges that have been added.
        If the superedge is in the set of superedges that have been removed, it is removed from that set instead.

        :param superedge: the superedge to add
        """
        if superedge not in self._e_minus:
            self._e_plus.add(superedge)
        else:
            self._e_minus.remove(superedge)

    def add_e_minus(self, superedge: Superedge):
        """
        Adds a superedge to the set of superedges that have been removed.
        If the superedge is in the set of superedges that have been added, it is removed from that set instead.

        :param superedge: the superedge to add
        """
        if superedge not in self._e_plus:
            self._e_minus.add(superedge)
        else:
            self._e_plus.remove(superedge)

    def has_updates(self) -> bool:
        """
        Returns True if there are any supernodes or superedges in any of the sets of the update quadruple,
        False otherwise.
        :return: True if there are any supernodes or superedges in the update quadruple
        """
        return bool(self._v_plus or self._v_minus or self._e_plus or self._e_minus)

    def clear(self):
        """
        Clears the update quadruple, removing all supernodes and superedges from its four sets.
        """
        self._v_plus.clear()
        self._v_minus.clear()
        self._e_plus.clear()
        self._e_minus.clear()

    def __str__(self):
        return f'UpdateQuadruple(v_plus={self._v_plus}, ' \
               f'v_minus={self._v_minus}, ' \
               f'e_plus={self._e_plus}, ' \
               f'e_minus={self._e_minus})'

    def __eq__(self, other):
        return self._v_plus == other.v_plus \
            and self._v_minus == other.v_minus \
            and self._e_plus == other.e_plus \
            and self._e_minus == other.e_minus