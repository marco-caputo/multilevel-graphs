from multilevel_graphs import Supernode, Superedge


class Superedge:
    __slots__ = ('tail', 'head', 'dec_e', 'attr')

    def __init__(self, tail: Supernode, head: Supernode, dec_e: set[Superedge] = set(), **attr):
        self.tail = tail
        self.head = head
        for e in dec_e:
            if e.tail not in self.tail.dec.V or e.head not in self.head.dec.V:
                raise ValueError('The supernodes of the superedge must be in the decontractible graph.')
        self.dec_e = dec_e
        self.attr = attr

    def add_edge(self, superedge: Superedge):
        """
        Adds a superedge to the superedge set represented by this superedge.

        :param superedge: the superedge to be added
        """
        self.dec.add_edge(superedge)

    def __eq__(self, other):
        return self.tail == other.tail and self.head == other.head

    def __hash__(self):
        return hash((self.tail, self.head))

    def __str__(self):
        return str(self.tail) + ' -> ' + str(self.head)
