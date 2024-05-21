from dec_graphs import Supernode, Superedge


class Superedge:
    __slots__ = ('tail', 'head', 'dec_e', 'attr')

    def __init__(self, tail: Supernode, head: Supernode, dec: set[Superedge] = set(), **attr):
        self.tail = tail
        self.head = head
        for e in dec:
            if e.tail not in self.tail.dec.V or e.head not in self.head.dec.V:
                raise ValueError('The supernodes of the superedge to be added must be included in tail and head'
                                 'decontractions respectively.')
        self.dec = dec
        self.attr = attr

    def add_edge(self, superedge: Superedge):
        """
        Adds a superedge to the superedge set represented by this superedge.
        If the superedge has a tail and head the key of which are already in the set, it will not be added again.

        :param superedge: the superedge to be added
        """
        if superedge.tail not in self.tail.dec.V or superedge.head not in self.head.dec.V:
            raise ValueError('The supernodes of the superedge to be added must be included in tail and head'
                             'decontractions respectively.')
        self.dec.add(superedge)

    def remove_edge(self, superedge: Superedge):
        """
        Removes a superedge from the superedge set represented by this superedge.
        If the superedge is not in the set, rise a KeyError.

        :param superedge: the superedge to be removed
        """
        self.dec.remove(superedge)

    def __eq__(self, other):
        return self.tail == other.tail and self.head == other.head

    def __hash__(self):
        return hash((self.tail, self.head))

    def __str__(self):
        return str(self.tail) + ' -> ' + str(self.head)
